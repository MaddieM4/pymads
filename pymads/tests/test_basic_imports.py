from pymads.extern import unittest

class TestImports(unittest.TestCase):
    def test_import_server(self):
        from pymads.pymads import DnsServer

    def test_import_error(self):
        from pymads.pymads import DnsError

    def test_import_sources(self):
        from pymads.sources import pymadsfile

    def test_import_filters(self):
        from pymads.filters import pymadsrr
