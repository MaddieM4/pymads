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
from pymads.response import Response

class Request(Packet):
    def __init__(self, qid=0, question=[], qtype=1, qclass=1):
        Packet.__init__(self,
            qid=qid,
            question=question,
            qtype=qtype,
            qclass=qclass,
        )

    def respond(self, code=0, records=[]):
        return Response(
            self.qid,
            self.question,
            self.qtype,
            self.qclass,
            code,
            records
        )

    def __repr__(self):
        return "<request question=%s qtype=%s qclass=%s>" % (
            self.question,
            self.qtype,
            self.qclass
        )

    def unpack(self, packet):
        Packet.unpack(self, packet)
        if self.flag_qr != 0 or self.flag_opcode != 0 or self.qdcount == 0:
            raise DnsError('FORMERR', "Invalid query")
