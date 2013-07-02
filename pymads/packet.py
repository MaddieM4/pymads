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
from persei import String, RawData
from pymads import const
from pymads import utils
from pymads.record import Record
from pymads.errors import DnsError, ErrorConverter

HEADER_LENGTH = 12

PARSE_GUARD = ErrorConverter(['FORMERR'])

def flag_property(position, size, doc):
    '''
    Handy trick we use to reduce duplicated flag code.

    Instead of creating a property with decorators, we use the property
    function, supplying it with lambdas that call self.getflag and
    self.setflag with the appropriate arguments.
    '''
    return property(
        fget = lambda self: self.getflag(position, size),
        fset = lambda self, value: self.setflag(position, size, value),
        doc  = doc
    )

class Packet(object):
    '''
    Represents a DNS packet, is the superclass of Response and Request.

    Handles all the responsibilities common across packet types, including
    flag properties.
    '''
    def __init__(self, 
            qid=0,
            flags=0,
            question=None,
            qtype=1,
            qclass=1,
            records=None
        ):
        self.qid      = qid
        self.flags    = flags
        self.question = question or []
        self.qtype    = const.get_code(const.RECORD_TYPES, qtype)
        self.qclass   = const.get_code(const.RECORD_TYPES, qclass)
        self.qdcount  = 1
        self.ancount  = 0
        self.nscount  = 0
        self.arcount  = 0
        self.records  = records or []

    @property
    def question(self):
        '''
        Domain name being queried, broken up into an array.

        For example, google.com -> ['google', 'com']
        '''
        return self._question

    @question.setter
    def question(self, value):
        '''
        Setter for self.question. Expects an iterable of strings.
        '''
        self._question = [
            String(String(x).export().lower())
            for x in value
        ]

    @property
    def name(self):
        '''
        Domain name being queried, as a single string.

        Example: 'google.com'
        '''
        return ".".join(x.export() for x in self.question)

    @name.setter
    def name(self, value):
        '''
        Setter for self.name. Expects a string.
        '''
        self.question = value.split('.')

    @property
    def records(self):
        '''
        All records that are in this packet's payload.
        '''
        return self._records

    @records.setter
    def records(self, value):
        '''
        Set the payload for the packet.

        Also recomputes the self.*_records properties.
        '''
        self._records = list(value)
        self.an_records = [r for r in self._records if r.rtype != 'NS']
        self.ns_records = [r for r in self._records if r.rtype == 'NS']
        self.ar_records = []
        self.ancount = len(self.an_records)
        self.nscount = len(self.ns_records)
        self.arcount = len(self.ar_records)

    # Flags data ------------------------------------------

    flag_qr = flag_property(15, 0x1,
        'qr : True if packet is a response'
    )

    flag_opcode = flag_property(11, 0xf,
        'opcode : Operation code'
    )

    flag_aa = flag_property(10, 0x1,
        'aa : Authoritative Answer'
    )

    flag_tc = flag_property(9, 0x1,
        'tc : Packet was truncated by UDP max packet size (512)'
    )

    flag_rd = flag_property(8, 0x1,
        'rd : Recursion desired'
    )

    flag_ra = flag_property(7, 0x1,
        'ra : Recursion available'
    )

    flag_z = flag_property(4, 0x8,
        'rcode : Response code'
    )

    flag_rcode = flag_property(0, 0xf,
        'rcode : Response code'
    )

    def getflag(self, position, size):
        '''
        Get a flag value from the flag data.

        position: int describing bit offset.
        size: mask, such as 0x1 for 1 bit, or 0xf for 4 bits
        '''
        return (self.flags >> position) & size

    def setflag(self, position, size, value):
        '''
        Set a flag value in the flag data.

        position: int describing bit offset.
        size: mask, such as 0x1 for 1 bit, or 0xf for 4 bits
        value: new value of the flag
        '''
        value = int(value) & size
        mask  = 0xffff - (size << position)
        self.flags = (self.flags & mask) | (value << position)

    # Packing and unpacking -------------------------------

    def pack(self):
        '''
        Returns serialized packet string.
        '''
        resources = []
        resources.extend(self.an_records)
        num_an = len(self.an_records)
        num_ns = num_ar = 0

        if self.flag_rcode == 0:
            resources.extend(self.ns_records)
            resources.extend(self.ar_records)
            num_ns = len(self.ns_records)
            num_ar = len(self.ar_records)

        pkt =  self.pack_header(num_an, num_ns, num_ar)
        pkt += self.pack_question()
        for resource in resources:
            pkt += resource.pack()
        return pkt

    def pack_header(self, ancount, nscount, arcount):
        """
        Serializes the header.
        """

        qdcount = 1

        hdr = struct.pack(
            "!HHHHHH",
            self.qid,
            self.flags,
            qdcount,
            ancount,
            nscount,
            arcount
        )
        return RawData(hdr)

    def pack_question(self):
        """
        Serializes the question data.
        """

        packed = utils.labels2str(self.question)
        packed += struct.pack(
            "!HH",
             self.qtype,
             self.qclass
        )
        return packed

    def unpack(self, packet):
        '''
        Parse a DNS packet and set object properties from it.
        '''

        packet = RawData(packet)
        with PARSE_GUARD:
            self.unpack_header(packet)
            self.unpack_body(packet)
        if self.qclass != 1:
            raise DnsError('FORMERR', "Invalid class: " + self.qclass)

    def unpack_header(self, packet):
        '''
        Parse the header data of a DNS packet.
        '''

        if len(packet) < HEADER_LENGTH:
            raise ValueError("Expected 12 byte header, got %r" % packet)
        (
            self.qid,
            self.flags,
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount
        ) = struct.unpack('!HHHHHH', packet[:HEADER_LENGTH].export())

    def unpack_body(self, packet):
        '''
        Parse the body data of a DNS packet.
        '''

        offset, self.question = utils.str2labels(packet, HEADER_LENGTH)
        self.qtype, self.qclass = struct.unpack(
            "!HH",
            packet[offset:offset+4].export()
        )
        offset += 4

        records = []
        # Ignore ADDITIONAL section for now
        for _ in range(self.ancount + self.nscount):# + self.arcount):
            # Read a record
            rec = Record('','0.0.0.0')
            offset = rec.unpack(packet, offset)
            records.append(rec)
        self.records = records

    # Misc ------------------------------------------------

    def __repr__(self):
        '''
        How repr(packet) behaves.

        Generally you will never see this in the wild unless you're doing
        weird stuff on purpose. It is rare that you will deal with a raw
        Packet, instead of its Request and Response subclasses.
        '''
        return "<packet qid=%d>" % (
            self.qid
        )
