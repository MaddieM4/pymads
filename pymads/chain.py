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

class Chain(object):
    '''
    Represents a source for DNS results, including filters
    '''
    def __init__(self, sources=None, filters=None):
        self.sources = sources or []
        self.filters = filters or []

    def get_from_sources(self, request):
        '''
        Returns a generator.
        '''
        for source in self.sources:
            for record in source.get(request):
                yield record

    def get(self, request):
        '''
        Retrieve DNS record set based on request.
        '''
        source = self.get_from_sources
        for filt in self.filters:
            filt.source = source
            source = filt.get
        return list(source(request))
