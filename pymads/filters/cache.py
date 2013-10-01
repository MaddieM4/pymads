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

from datetime import datetime, timedelta

class CacheFilter(object):
    '''
    Doesn't hit the next layer of filtering if we already retrieved the data.
    '''

    def __init__(self):
        self.cache = {}

    def get(self, request):
        key = request.pack_question()
        now = datetime.now()
        if key in self.cache and now < min(r.ttl for r in self.cache[key]):
            return self.cache[key]
        else:
            result = list(self.source(request))
            for r in result:
                r.ttl = now + timedelta(0, r.rttl)
            self.cache[key] = result
            return result
