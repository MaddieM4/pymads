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
import logging

from pymads import const

class DnsError(Exception):
    '''
    DNS-related error that can be turned into an error response by the
    server when caught.
    '''
    def __init__(self, errtype, *args):
        self.code  = const.get_code( const.ERROR_CODES, errtype)
        self.label = const.get_label(const.ERROR_CODES, errtype)
        Exception.__init__(self, self.label, self.code, *args)

class ErrorConverter(object):
    '''
    Converts all non-DnsError exceptions to DnsError exceptions.
    '''
    def __init__(self, args, logger_name='server'):
        '''
        These args are used as the first args in the DnsError constructor
        whenever we convert a non-DnsError exception to a DnsError.
        '''
        self.args = tuple(args)
        self.log = logging.getLogger(logger_name)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            return

        if isinstance(exc_val, exc_type):
            exc = exc_val
        else:
            exc = exc_type(exc_val)

        if not isinstance(exc_val, DnsError):
            self.log.debug(''.join(
                traceback.format_exception(
                    exc_type,
                    exc_val,
                    exc_tb,
                )
            ))
            new_args = self.args + exc.args
            raise DnsError(*new_args)
