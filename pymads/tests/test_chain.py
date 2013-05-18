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
        chain  = Chain([source])
        self.assertEqual(
            chain.get(hostname),
            set([record])
        )
        self.assertEqual(chain.get('not'+hostname), set())

    def test_jsonsource(self):
        from pymads.sources.json import JSONSource

        path     = 'examples/sushi.json'
        hostname = 'sushi.org'
        ip_addr  = '5.4.3.2'

        source  = JSONSource(path)
        chain   = Chain([source])
        results = chain.get(hostname)

        self.assertEqual(
            results.pop().rdata,
            ip_addr
        )
        self.assertEqual(chain.get('not'+hostname), set())
