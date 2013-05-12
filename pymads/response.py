from __future__ import absolute_import

import struct
from pymads import utils

def byteify(obj):
    try:
        return bytes(obj, 'utf-8')
    except:
        return str(obj)

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
            pkt += self.format_resource(resource)
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

    def format_resource(self, resource):
        """Formats the resource fields to be used in the response packet"""

        r  = utils.labels2str(self.request.question)
        r += struct.pack(
            "!HHIH",
             resource.rtypecode,
             resource.rclasscode,
             resource.rttl,
             len(resource.rdata)
        )
        r += byteify(resource.rdata)
        return r
