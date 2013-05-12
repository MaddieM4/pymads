from pymads.extern import unittest
from pymads.chain  import Chain
from pymads.record import Record

class TestChains(unittest.TestCase):
    ''' Test various aspects of chains. '''

    def test_dictsource(self):
        from pymads.sources.dict import DictSource

        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        source = DictSource({hostname: [record]})
        self.chain = Chain([source])
        self.assertEqual(
            self.chain.get(hostname),
            set([record])
        )
        self.assertEqual(self.chain.get('not'+hostname), set())
