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
        host_data = dig(record.domain_name, test_host, test_port)
        success_text = '''
;; ANSWER SECTION:
%s.\t\t%d\t%s\t%s\t%s
''' % (record.domain_name, record.rttl, record.rclass, record.rtype, record.rdata)

        self.assertIn(
            success_text,
            host_data
        )

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

    def test_error_NXDOMAIN(self):
        '''
        Observe how server reacts when asked for something it doesn't know.
        '''
        host_data = dig('sushi.org', test_host, test_port)
        self.assertIn(
            '->>HEADER<<- opcode: QUERY, status: NXDOMAIN',
            host_data
        )
        self.assertIn(
            'QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0',
            host_data
        )

    def test_error_FORMERR(self):
        '''
        Observe how server reacts when sent a structurally invalid request.
        '''
        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        self.setup_chain(record)

        import socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((test_host, test_port + 1))
        self.socket.settimeout(1)

        self.socket.sendto(b'Random garbage', (test_host, test_port))
        response = self.socket.recv(512)

        if str == bytes:
            rcode = ord(response[3]) & 0xf
        else:
            rcode = response[3] & 0xf

        self.assertEqual(
            rcode,
            get_error_code('FORMERR')
        )

    def tearDown(self):
        self.server.stop()
        self.thread.join(2)
