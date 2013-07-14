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

class DictSource(object):
    '''
    Simplest source. All data in memory, in the form of a dict.

    Data format:
        {
            'mydomain.com' : [
                <pymads.record.Record>
            ],
            'myotherdomain.com' : [
                <pymads.record.Record>,
                <pymads.record.Record>,
            ]
        }
    '''
    def __init__(self, data = {}):
        self.data = dict(data)

    def get(self, request):
        if isinstance(req_in, Request):
            name = request.name
        else:
            name = request
        return self.data.get(name, [])
