from __future__ import absolute_import

import struct
from pymads.errors import *

class Request(object):
    def __init__(self, qid, question, qtype, qclass, src_addr):
        self.qid      = qid
        self.question = list(map(lambda x: x.lower(), question))
        self.qtype    = qtype
        self.qclass   = qclass
        self.src_addr = src_addr

    def __repr__(self):
        return "<request question=%s qtype=%s qclass=%s>" % (
            self.question,
            self.qtype,
            self.qclass
        )

def parse(packet, src_addr):
    ''' Parse a text query and return a Request object '''

    hdr_len = 12
    header = packet[:hdr_len]
    qid, flags, qdcount, _, _, _ = struct.unpack('!HHHHHH', header)
    qr = (flags >> 15) & 0x1
    opcode = (flags >> 11) & 0xf
    rd = (flags >> 8) & 0x1
    #print "qid", qid, "qdcount", qdcount, "qr", qr, "opcode", opcode, "rd", rd
    if qr != 0 or opcode != 0 or qdcount == 0:
        raise DnsError("Invalid query")
    body = packet[hdr_len:]
    labels = []
    offset = 0
    while True:
        label_len, = struct.unpack('!B', body[offset:offset+1])
        offset += 1
        if label_len & 0xc0:
            raise DnsError("Invalid label length %d" % label_len)
        if label_len == 0:
            break
        label = body[offset:offset+label_len]
        offset += label_len
        labels.append(label)
    qtype, qclass= struct.unpack("!HH", body[offset:offset+4])
    if qclass != 1:
        raise DnsError("Invalid class: " + qclass)
    return Request(qid, labels, qtype, qclass, src_addr)
