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

from __future__ import absolute_import

import struct
from pymads import utils

class Response(object):
    """ Represents a response packet """

    def __init__(self, request, code, records = []): 
        self.request    = request
        self.code       = code
        self.records    = records
        self.an_records = [r for r in records if r.rtype != 'NS']
        self.ns_records = [r for r in records if r.rtype == 'NS']
        self.ar_records = [] # TODO

    def export(self):
        """Formats the packet response"""
        
        resources = []
        resources.extend(self.an_records)
        num_an = len(self.an_records)
        num_ns = num_ar = 0

        if self.code == 0:
            resources.extend(self.ns_records)
            resources.extend(self.ar_records)
            num_ns = len(self.ns_records)
            num_ar = len(self.ar_records)

        pkt =  self.format_header(num_an, num_ns, num_ar)
        pkt += self.format_question()
        for resource in resources:
            pkt += resource.export()
        return pkt

    def format_header(self, ancount, nscount, arcount):
        """Formats the header to be used in the response packet"""

        flags = 0
        flags |= (1 << 15)
        flags |= (1 << 10)
        flags |= (self.code & 0xf)
        hdr = struct.pack(
            "!HHHHHH",
            self.request.qid,
            flags,
            1,
            ancount,
            nscount,
            arcount
        )
        return hdr

    def format_question(self):
        """Formats the question field to be used in the response packet"""

        q = utils.labels2str(self.request.question)
        q += struct.pack(
            "!HH",
             self.request.qtype,
             self.request.qclass
        )
        return q
