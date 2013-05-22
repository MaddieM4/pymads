from pymads.errors import *
from pymads.extern import unittest

class TestErrors(unittest.TestCase):

    def test_int_constructor(self):
        e = DnsError(0)
        self.assertEquals(e.code,  0)
        self.assertEquals(e.error, 'NOERROR')

        e = DnsError(1)
        self.assertEquals(e.code,  1)
        self.assertEquals(e.error, 'FORMERR')

        e = DnsError(5)
        self.assertEquals(e.code,  5)
        self.assertEquals(e.error, 'REFUSED')

        msg =  "You're gonna have one."
        e = DnsError(0xe, msg)
        self.assertEquals(e.code,  0xe)
        self.assertEquals(e.error, 'BADTIME')
        self.assertEquals(e.args, ('BADTIME', 0xe, msg))

    def test_str_constructor(self):
        e = DnsError('NOERROR')
        self.assertEquals(e.code, 0)
        self.assertEquals(e.error, 'NOERROR')        

        e = DnsError('REFUSED')
        self.assertEquals(e.code,  5)
        self.assertEquals(e.error, 'REFUSED')

        msg =  "You're gonna have one."
        e = DnsError('BADTIME', msg)
        self.assertEquals(e.code,  0xe)
        self.assertEquals(e.error, 'BADTIME')
        self.assertEquals(e.args, ('BADTIME', 0xe, msg))

    def test_repr(self):
        self.assertEquals(
            repr(DnsError(3)),
            "DnsError('NXDOMAIN', 3)"
        )
        self.assertEquals(
            repr(DnsError(2, "Wrench in the works")),
            "DnsError('SERVFAIL', 2, 'Wrench in the works')"
        )

class TestConverter(unittest.TestCase):
    def test_dnserr(self):
        with self.assertRaises(DnsError) as assertion:
            with ErrorConverter((3,)).quiet():
                raise DnsError(1)
        
        self.assertEquals(
            repr(assertion.exception),
            "DnsError('FORMERR', 1)"
        )

    def test_diverr(self):
        with self.assertRaises(DnsError) as assertion:
            with ErrorConverter((3,)).quiet():
                return 1/0
        
        # Split into several parts - error messages differ by
        # version of Python
        exc = assertion.exception
        self.assertIn(
            "DnsError('NXDOMAIN', 3, '",
            repr(exc)
        )
        self.assertIn(
            "division or modulo by zero')",
            repr(exc)
        )

    def test_customerr(self):
        with self.assertRaises(DnsError) as assertion:
            with ErrorConverter((1,)).quiet():
                raise Exception()
        
        self.assertEquals(
            repr(assertion.exception),
            "DnsError('FORMERR', 1)"
        )

        with self.assertRaises(DnsError) as assertion:
            with ErrorConverter((1,)).quiet():
                raise Exception('ABC')
        
        self.assertEquals(
            repr(assertion.exception),
            "DnsError('FORMERR', 1, 'ABC')"
        )

        with self.assertRaises(DnsError) as assertion:
            with ErrorConverter((1,)).quiet():
                raise Exception('ABC', 123)
        
        self.assertEquals(
            repr(assertion.exception),
            "DnsError('FORMERR', 1, 'ABC', 123)"
        )

    def test_badinit(self):
        # Someone forgot that the first argument is an iterable...
        with self.assertRaises(TypeError) as assertion:
            with ErrorConverter(1).quiet():
                raise Exception()
        
        self.assertIn(
            "'int' object is not iterable",
            repr(assertion.exception)
        )
