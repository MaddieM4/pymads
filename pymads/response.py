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

from pymads.packet import Packet

class Response(Packet):
    """ Represents a response packet """

    def __init__(self, qid=0, question=[], qtype=1, qclass=1, code=0, records = []): 
        Packet.__init__(self,
            qid=qid,
            question=question,
            qtype=qtype,
            qclass=qclass,
            records=records
        )
        self.flag_qr = True
        self.flag_response = True
        self.flag_rcode = code

    def __repr__(self):
        return "<response question=%s rcode=%d records=%r>" % (
            self.question,
            self.flag_rcode,
            self.records
        )
