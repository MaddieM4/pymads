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

from pymads.extern import unittest
from pymads.sources.dns import DnsSource, MultiDNS

class TestRecursion(unittest.TestCase):
    def setUp(self):
        self.source = DnsSource() # Uses 8.8.8.8 by default

    def looks_about_right(self, domain, results):
        self.assertTrue(len(results) > 0)
        for record in results:
            self.assertEqual(record.domain_name, domain)

    def test_recursion(self):
        self.looks_about_right(
            'google.com',
            self.source.get_domain_string('google.com')
        )

    def test_multidns(self):
        addr = self.source.remote_addr
        mdns = MultiDNS()

        mdns.add(self.source)
        self.assertEqual(self.source, mdns.get_source(addr))

        self.looks_about_right(
            'google.com',
            mdns.get_domain_string('google.com', addr)
        )

        # What about other servers?
        addr2 = ('8.8.4.4', 53)
        self.looks_about_right(
            'google.com',
            mdns.get_domain_string('google.com', addr2)
        )

        # And we aren't throwing things away after we make them
        self.assertEqual(
            mdns.get_source(addr2),
            mdns.get_source(addr2)
        )
