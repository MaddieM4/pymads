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
            chain.get_domain_string(hostname),
            [record]
        )
        self.assertEqual(chain.get_domain_string('not'+hostname), [])

    def test_jsonsource(self):
        from pymads.sources.json import JSONSource

        path     = 'examples/sushi.json'
        hostname = 'sushi.org'
        ip_addr  = '5.4.3.2'

        source  = JSONSource(path)
        chain   = Chain([source])
        results = chain.get_domain_string(hostname)

        self.assertEqual(
            results.pop().rdata,
            ip_addr
        )
        self.assertEqual(chain.get_domain_string('not'+hostname), [])

    def test_cachefilter(self):
        from pymads.sources.dict  import DictSource
        from pymads.filters.cache import CacheFilter

        hostname = 'example.com'
        ip_addr  = '9.9.9.9'
        record   = Record(hostname, ip_addr)

        source = DictSource({hostname: [record]})
        filter = CacheFilter()
        chain  = Chain([source], [filter])

        self.assertEqual(
            chain.get_domain_string(hostname),
            [record]
        )

        # Clear out the source and see if Pepperidge Cache remembers
        source.data = {}

        self.assertEqual(
            chain.get_domain_string(hostname),
            [record]
        )

    def test_cachesetexpired(self):
        from pymads.sources.dict  import DictSource
        from pymads.filters.cache import CacheFilter

        hostname1 = 'example.com'
        hostname2 = 'example.org'
        hostname3 = 'example.net'
        ip_addr = '9.9.9.9'
        expired = Record(hostname1, ip_addr, rttl=0)
        record1 = Record(hostname1, ip_addr, rttl=1800)
        record3 = Record(hostname3, ip_addr, rttl=1800)

        source = DictSource({
            hostname1: [expired],
            hostname2: [record1, expired],
            hostname3: [record3],
        })
        filter = CacheFilter()
        chain  = Chain([source], [filter])

        self.assertEqual(chain.get_domain_string(hostname1), [expired])
        self.assertEqual(chain.get_domain_string(hostname2), [record1, expired])
        self.assertEqual(chain.get_domain_string(hostname3), [record3])

        # The record has expired
        source.data = {}

        self.assertEqual(chain.get_domain_string(hostname1), [])
        self.assertEqual(chain.get_domain_string(hostname2), [])
        self.assertEqual(chain.get_domain_string(hostname3), [record3])
