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
from pymads.sources.dns import DnsSource

class TestRecursion(unittest.TestCase):
    def setUp(self):
        self.source = DnsSource() # Uses 8.8.8.8 by default

    def test_recursion(self):
        google = self.source.get('google.com')

        self.assertTrue(len(google) > 0)
        for record in google:
            self.assertEqual(record.domain_name, 'google.com')
