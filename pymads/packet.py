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
from pymads.errors import *

HEADER_LENGTH = 12

ParseGuard = ErrorConverter(['FORMERR'])

def stringify(obj):
    if hasattr(obj, 'decode'):
        return obj.decode()
    else:
        return str(obj)

class Packet(object):
    def __init__(self, 
            qid=0,
            flags=0,
            question=[],
            qtype=1,
            qclass=1,
            src_addr=tuple()
        ):
        self.qid      = qid
        self.flags    = flags
        self.question = question
        self.qtype    = qtype
        self.qclass   = qclass
        self.src_addr = src_addr

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, value):
        self._question = list(map(lambda x: x.lower(), value))

    @property
    def name(self):
        return ".".join(stringify(x) for x in self.question)

    @name.setter
    def name(self, value):
        self.question = value.split('.')

    # Flags data ------------------------------------------

    # qr : True if packet is a response
    @property
    def flag_qr(self):
        return self.getflag(15, 0x1)

    @flag_qr.setter
    def flag_qr(self, value):
        self.setflag(15, 0x1, value)

    # opcode : Operation code
    @property
    def flag_opcode(self):
        return self.getflag(11, 0xf)

    @flag_opcode.setter
    def flag_opcode(self, value):
        self.setflag(11, 0xf, value)

    # rd : Cargo culting for now (TODO : RESEARCH)
    @property
    def flag_rd(self):
        return self.getflag(8, 0xf)

    @flag_rd.setter
    def flag_rd(self, value):
        self.setflag(8, 0xf, value)

    # rcode : Response code
    @property
    def flag_rcode(self):
        return self.getflag(0, 0x1)

    @flag_rcode.setter
    def flag_rcode(self, value):
        self.setflag(0, 0x1, value)

    def getflag(self, position, size):
        return (self.flags >> position) & size

    def setflag(self, position, size, value):
        value = int(value) & size
        mask  = 0xffff - (size << position)
        self.flags = (self.flags & mask) | (value << position)

    def __repr__(self):
        return "<packet qid=%d from %r>" % (
            self.qid,
            self.src_addr
        )

    def pack(self):
        ''' Return packet string for request '''
        resources = []
        resources.extend(self.an_records)
        num_an = len(self.an_records)
        num_ns = num_ar = 0

        if self.code == 0:
            resources.extend(self.ns_records)
            resources.extend(self.ar_records)
            num_ns = len(self.ns_records)
            num_ar = len(self.ar_records)

        pkt =  self.pack_header(num_an, num_ns, num_ar)
        pkt += self.pack_question()
        for resource in resources:
            pkt += resource.pack()
        return pkt

    def unpack(self, packet):
        ''' Parse a DNS packet and set object properties from it '''

        with ParseGuard:
            self.unpack_header(packet[:HEADER_LENGTH])
            self.unpack_body(packet[HEADER_LENGTH:])
        if self.qclass != 1:
            raise DnsError('FORMERR', "Invalid class: " + qclass)

    def unpack_header(self, header):
        ''' Parse the header data of a DNS packet. '''

        if len(header) != HEADER_LENGTH:
            raise ValueError("Expected 12 byte header, got %r" % header)
        self.qid, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount = struct.unpack('!HHHHHH', header)

    def unpack_body(self, body):
        ''' Parse the body data of a DNS packet. '''

        labels = []
        offset = 0
        while True:
            label_len, = struct.unpack('!B', body[offset:offset+1])
            offset += 1
            if label_len & 0xc0:
                raise DnsError('FORMERR', "Invalid label length %d" % label_len)
            if label_len == 0:
                break
            label = body[offset:offset+label_len]
            offset += label_len
            labels.append(label)
        self.qtype, self.qclass= struct.unpack("!HH", body[offset:offset+4])
        self.question = labels
