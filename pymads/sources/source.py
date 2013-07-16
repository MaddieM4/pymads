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

class Source(object):
    '''
    A source for pymads DNS records
    '''

    def get(self, request):
        '''
        Takes request, returns array of pymads records.
        '''
        raise NotImplementedError('Source subclass must define get()')

    def get_domain_string(self, domain):
        '''
        Takes domain name string, and return pymads records
        '''
        request = Request()
        request.name = domain
        return self.get(request)

