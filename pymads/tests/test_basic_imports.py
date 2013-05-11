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

    def test_import_sources(self):
        from pymads.sources import pymadsfile
        from pymads.sources.dict import DictSource

    def test_import_filters(self):
        from pymads.filters import pymadsrr
