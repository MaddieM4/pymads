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

import traceback

class DnsError(Exception):
    def __init__(self, errtype, *args):
        if isinstance(errtype, int):
            self.code  = errtype
            self.error = get_error_name(self.code)
        else:
            self.error = errtype
            self.code  = get_error_code(self.error)
        Exception.__init__(self, self.error, self.code, *args)

class ErrorConverter(object):
    '''
    Converts all non-DnsError exceptions to DnsError exceptions.
    '''
    def __init__(self, args, tb_stream='stderr'):
        '''
        These args are used as the first args in the DnsError constructor
        whenever we convert a non-DnsError exception to a DnsError.
        '''
        self.args  = tuple(args)
        self._quiet = False
        if isinstance(tb_stream, str):
            import sys
            self.tb_stream = getattr(sys, tb_stream)
        else:
            self.tb_stream = tb_stream

    def quiet(self, value = True):
        self._quiet = value
        return self

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        quiet, self._quiet = self._quiet, False
        if not exc_type:
            return

        if isinstance(exc_val, exc_type):
            e = exc_val
        else:
            e = exc_type(exc_val)

        if not isinstance(exc_val, DnsError):
            if self.tb_stream and not quiet:
                traceback.print_exception(
                    exc_type,
                    exc_val,
                    exc_tb,
                    file=self.tb_stream
                )
            new_args = self.args + e.args
            raise DnsError(*new_args)

def get_error_name(code):
    '''
    Determine a DNS error's name by its numeric code.
    '''
    if code < 0 or code > 0xe:
        raise ValueError("Code %d out of range (0-14)")
    for (key, value) in ERROR_CODES.items():
        if value == code:
            return key

def get_error_code(name):
    '''
    Determine a DNS error's numeric code by its name.
    '''
    return ERROR_CODES[name]

ERROR_CODES = {
    'NOERROR' : 0x0, # no error
    'FORMERR' : 0x1, # format error
    'SERVFAIL': 0x2, # server failure
    'NXDOMAIN': 0x3, # name error
    'NOTIMPL' : 0x4, # not implemented
    'REFUSED' : 0x5, # connection refused
    'YXDOMAIN': 0x6, # domain name should not exist
    'YXRRSET' : 0x7, # resource record set should not exist
    'NXRRSET' : 0x8, # rrset does not exist
    'NOTAUTH' : 0x9, # not authoritative for zone
    'NOTZONE' : 0xa, # name not in zone
    'BADVERS' : 0xb, # bad extension mechanism for version
    'BADSIG'  : 0xc, # bad signature
    'BADKEY'  : 0xd, # bad key
    'BADTIME' : 0xe, # bad timestamp
}
