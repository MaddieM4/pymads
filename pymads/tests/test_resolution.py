import threading

from pymads.extern import unittest
from pymads.server import DnsServer
from pymads.chain  import Chain
from pymads.record import Record
from pymads.tests.dig import dig

test_host = '127.0.0.1'
test_port = 53000

class TestResolution(unittest.TestCase):
    ''' Full-stack integration test '''

    def setUp(self):
        self.server = DnsServer(
                                listen_host = test_host,
                                listen_port = test_port
                      )
        self.thread = threading.Thread(target=self.server.serve)
        self.thread.start()

    def test_ram_chain(self):
        from pymads.sources.dict import DictSource

        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        source = DictSource({hostname: [record]})
        self.chain = Chain([source])
        self.server.config['chains'] = [self.chain]
        host_data = dig(hostname, test_host, test_port)
        success_text = '''
;; ANSWER SECTION:
%s.\t\t1800\tIN\tA\t%s
''' % (hostname, ip_addr)

        self.assertIn(
            success_text,
            host_data
        )

    def tearDown(self):
        self.server.stop()
        self.thread.join(2)
