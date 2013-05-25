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
import threading

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

    def do_test_record(self, record):
        '''
        Test that a record is retrievable.
        '''
        host_data = self.dig(record.domain_name)
        success_text = '''
;; ANSWER SECTION:
%s.\t\t%d\t%s\t%s\t%s
''' % (record.domain_name, record.rttl, record.rclass, record.rtype, record.rdata)

        self.assertIn(
            success_text,
            host_data
        )

    def dig(self, domain_name):
        return dig(domain_name, test_host, test_port)

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

    def dig(self, domain_name):
        '''
        IPv6 version of dig function.
        '''
        return dig(domain_name, test_host_ipv6[0], test_port)

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
