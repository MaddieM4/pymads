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

def stringify(obj):
    if hasattr(obj, 'decode'):
        return obj.decode()
    else:
        return str(obj)

class Request(object):
    def __init__(self, qid, question, qtype, qclass, src_addr):
        self.qid      = qid
        self.question = list(map(lambda x: x.lower(), question))
        self.qtype    = qtype
        self.qclass   = qclass
        self.src_addr = src_addr

    @property
    def name(self):
        return ".".join(stringify(x) for x in self.question)

    def __repr__(self):
        return "<request question=%s qtype=%s qclass=%s>" % (
            self.question,
            self.qtype,
            self.qclass
        )

def parse(packet, src_addr):
    ''' Parse a text query and return a Request object '''

    try:
        hdr_len = 12
        header = packet[:hdr_len]
        qid, flags, qdcount, _, _, _ = struct.unpack('!HHHHHH', header)
        qr = (flags >> 15) & 0x1
        opcode = (flags >> 11) & 0xf
        rd = (flags >> 8) & 0x1
        #print "qid", qid, "qdcount", qdcount, "qr", qr, "opcode", opcode, "rd", rd
        if qr != 0 or opcode != 0 or qdcount == 0:
            raise DnsError('FORMERR', "Invalid query")
        body = packet[hdr_len:]
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
        qtype, qclass= struct.unpack("!HH", body[offset:offset+4])
    except Exception as e:
        if isinstance(e, DnsError):
            raise
        else:
            raise DnsError("FORMERR", "Unknown request parsing error")
    if qclass != 1:
        raise DnsError('FORMERR', "Invalid class: " + qclass)
    return Request(qid, labels, qtype, qclass, src_addr)
