'''
This file is part of Pymads.

Pymads is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pymads is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Pymads.  If not, see <http://www.gnu.org/licenses/>
'''

from __future__ import unicode_literals
import re
import threading

from persei import RawData

from pymads.errors import *
from pymads.extern import unittest
from pymads.server import DnsServer
from pymads.chain  import Chain
from pymads.record import Record
from pymads.sources.dict import DictSource
from pymads.tests.dig import dig

test_host = '127.0.0.1'
test_port = 53000

test_host_ipv6 = ('::1', 0, 1)

class TestResolution(unittest.TestCase):
    ''' Full-stack integration test '''

    def setUp(self):
        self.server = DnsServer(
                                listen_host = test_host,
                                listen_port = test_port,
                      )
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve)
        self.thread.start()

    def setup_chain(self, record):
        '''
        Set up chain with a single source, containing a single Record.
        '''
        source = DictSource({record.domain_name: [record]})
        self.chain = Chain([source])
        self.server.config['chains'] = [self.chain]

    def do_test_record(self, *records, **kwargs):
        '''
        Test that a record is retrievable.
        '''
        query_domain = records[0].domain_name
        host_data = self.dig(query_domain, **kwargs)

        answer_string = '\n;; ANSWER SECTION:\n'
        self.assertIn(answer_string, host_data)

        start_index = host_data.index(answer_string)
        end_index   = host_data.index('\n\n;;', start_index)
        answer_section = host_data[start_index:end_index]
        answers = [
            re.sub('\s+', '\t', s)
            for s in answer_section.split('\n')[2:]
        ]

        for record in records:
            success_text = str(record)

            self.assertIn(
                success_text,
                answers
            )

            answers.remove(success_text)

        if answers:
            raise Exception(answer_section)
        self.assertEquals(answers, [])

    def dig(self, domain_name, qtype='ANY', extra=[]):
        return dig(domain_name, test_host, test_port,
                     timeout=1, retry=0, qtype=qtype, extra=extra)

    def test_A(self):
        '''
        Attempt to store and resolve an A record.
        '''
        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        self.setup_chain(record)
        self.do_test_record(record)

    def test_AAAA(self):
        '''
        Attempt to store and resolve an AAAA record.
        '''
        record = Record(
            'example.com',
            'abcd::1234',
            rtype = 'AAAA'
        )

        self.setup_chain(record)
        self.do_test_record(record)

    def test_CNAME(self):
        from pymads.sources.dns import DummyDnsSource

        # Response from 8.8.8.8 for www.theuselessweb.com
        packet = RawData((0x0,0x1,0x81,0x80,0x0,0x1,0x0,0x3,0x0,0x0,0x0,0x0,0x3,0x77,0x77,0x77,0xd,0x74,0x68,0x65,0x75,0x73,0x65,0x6c,0x65,0x73,0x73,0x77,0x65,0x62,0x3,0x63,0x6f,0x6d,0x0,0x0,0x1,0x0,0x1,0xc0,0xc,0x0,0x5,0x0,0x1,0x0,0x0,0xe,0x10,0x0,0x37,0x3,0x77,0x77,0x77,0xd,0x74,0x68,0x65,0x75,0x73,0x65,0x6c,0x65,0x73,0x73,0x77,0x65,0x62,0x3,0x63,0x6f,0x6d,0x14,0x73,0x33,0x2d,0x77,0x65,0x62,0x73,0x69,0x74,0x65,0x2d,0x75,0x73,0x2d,0x65,0x61,0x73,0x74,0x2d,0x31,0x9,0x61,0x6d,0x61,0x7a,0x6f,0x6e,0x61,0x77,0x73,0xc0,0x1e,0xc0,0x33,0x0,0x5,0x0,0x1,0x0,0x0,0x0,0x3c,0x0,0x2,0xc0,0x49,0xc0,0x49,0x0,0x1,0x0,0x1,0x0,0x0,0x0,0x3c,0x0,0x4,0xcd,0xfb,0xf2,0x83))

        self.chain = Chain([DummyDnsSource(packet)])
        self.server.config['chains'] = [self.chain]

        # Test input parsing
        uwstr = 'www.theuselessweb.com'
        awstr = 's3-website-us-east-1.amazonaws.com'
        ipstr = '205.251.242.131'
        fstr  = uwstr + '.' + awstr

        expected_records = [
            Record(uwstr,fstr, 'CNAME',3600),
            Record(fstr, awstr,'CNAME',60),
            Record(awstr,ipstr,'A'    ,60),
        ]

        records = self.chain.get_domain_string('www.theuselessweb.com')
        self.assertEquals(
            records,
            expected_records,
        )

        self.do_test_record(*expected_records)

    def test_SOA(self):
        '''
        Attempt to store and resolve a SOA record.
        '''
        from pymads.record import SOAType

        keys = ('mname', 'rname',
            'serial', 'refresh', 'retry', 'expire', 'minimum')
        values = ('ns.example.com', 'dns-admin.example.com',
            2003080800, 172800, 1209600, 900, 3600)

        # Test every valid input
        for rdata in (values, dict(zip(keys, values)), SOAType(*values)):
            record = Record('example.com', rdata, rtype = 'SOA')

            self.setup_chain(record)
            self.do_test_record(record)

        # Test invalid dict input
        self.assertRaises(
            TypeError,
            lambda: Record('example.com', dict(zip(keys, values[:-1])), 'SOA')
        )

    def test_async(self):
        '''
        Run server and consumer threads seperately.
        '''
        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        self.setup_chain(record)
        # Use the server's own default consumer, just in another thread
        self.server.config['own_consumer'] = False
        self.thread_cons = threading.Thread(
            target=self.server._default_consumer.listen
        )
        self.thread_cons.start()
        self.do_test_record(record)

    def test_recursive(self):
        '''
        Test responses where recursion is wanted and unwanted.
        '''
        from pymads.sources.dns import DnsSource

        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)
        self.setup_chain(record)

        record_official = Record(hostname, '93.184.216.119', rttl=86400)

        # Use b.iana-servers.net for consistent TTL
        source = DnsSource(remote=('b.iana-servers.net', 53))
        self.chain.sources.append(source)

        # Test where recursion is wanted
        self.do_test_record(record, record_official, qtype='A')
        # Test where recursion is unwanted
        # TODO : use source flags
        self.do_test_record(record, record_official, qtype='A',
            extra=['+norecurse'])

    def test_error_SERVFAIL(self):
        '''
        Observe how server reacts when a source completely fails with 
        an exception.
        '''
        class BadSource(object):
            def get(self, *args):
                return 1/0

        self.chain = Chain([BadSource()])
        self.server.config['chains'] = [self.chain]
        self.server.debug = False
        host_data = self.dig('sushi.org')
        self.assertIn(
            'SERVFAIL',
            host_data
        )

    def test_error_NXDOMAIN(self):
        '''
        Observe how server reacts when asked for something it doesn't know.
        '''
        host_data = self.dig('sushi.org')
        self.assertIn(
            '->>HEADER<<- opcode: QUERY, status: NXDOMAIN',
            host_data
        )
        self.assertIn(
            'QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0',
            host_data
        )

    def make_socket(self):
        '''
        Make UDP socket for more manual testing than dig.
        '''
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((test_host, test_port + 1))
        s.settimeout(1)
        return s

    def test_error_FORMERR(self):
        '''
        Observe how server reacts when sent a structurally invalid request.
        '''
        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        self.setup_chain(record)

        self.socket = self.make_socket()
        self.socket.sendto(
            b'Random garbage',
            self.server.socket.getsockname()
        )
        response = self.socket.recv(512)

        if str == bytes:
            rcode = ord(response[3]) & 0xf
        else:
            rcode = response[3] & 0xf

        self.assertEqual(
            rcode,
            const.ERROR_CODES['FORMERR']
        )

    def tearDown(self):
        self.server.stop()
        self.thread.join(2)
        if hasattr(self, 'socket'):
            self.socket.close()

class TestResolutionIPv6(TestResolution):
    ''' Full-stack integration test - IPv6 '''

    def setUp(self):
        self.server = DnsServer(
                                listen_host = test_host_ipv6,
                                listen_port = test_port,
                      )
        self.server.bind()
        self.thread = threading.Thread(target=self.server.serve)
        self.thread.start()

    def dig(self, domain_name, qtype='ANY', extra=[]):
        '''
        IPv6 version of dig function.
        '''
        return dig(domain_name, test_host_ipv6[0], test_port,
                     timeout=1, retry=0, qtype=qtype, extra=extra)

    def make_socket(self):
        '''
        IPv6 version of test socket construction.
        '''
        host, flow, scope = test_host_ipv6
        addr = (host, test_port+1, flow, scope)

        import socket
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.bind(addr)
        s.settimeout(1)
        return s
