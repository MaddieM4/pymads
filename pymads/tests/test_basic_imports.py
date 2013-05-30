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

class TestImports(unittest.TestCase):
    def test_import_server(self):
        from pymads.server import DnsServer

    def test_import_error(self):
        from pymads.errors import DnsError

    def test_import_chain(self):
        from pymads.chain import Chain

    def test_import_request(self):
        from pymads.request import Request

    def test_import_response(self):
        from pymads.response import Response

    def test_import_packet(self):
        from pymads.packet import Packet

    def test_import_sources(self):
        from pymads.sources.json import JSONSource
        from pymads.sources.dict import DictSource
        from pymads.sources.dns  import DnsSource

    def test_import_filters(self):
        from pymads.filters.cache import CacheFilter
