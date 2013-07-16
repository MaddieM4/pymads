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

from __future__ import print_function

import socket
from persei import RawData
from pymads.request import Request
from pymads.response import Response
from pymads.sources.source import Source

class DnsSource(Source):
    '''
    Used for recursive resolution. Pulls data from external DNS server.
    '''
    def __init__(self, local =('0.0.0.0', 9822),
                       remote=('8.8.8.8', 53),
                       retries = 5):

        self.local_addr  = local
        self.remote_addr = remote
        self.appid = 0
        self.retries = retries

    def make_socket(self):
        if '.' in self.local_addr[0]:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.socket.bind(self.local_addr)
        self.socket.settimeout(1)

    def close_socket(self):
        if hasattr(self, 'socket'):
            self.socket.close()
            self.socket = None

    def exchange(self, request):
        '''
        Takes a Request object, returns a Response object from remote.
        '''
        req_pkt = request.pack()

        resp_pkt = self._exchange_data(req_pkt)

        resp = Response()
        resp.unpack(resp_pkt)
        return resp

    def _exchange_data(self, req_pkt):
        '''
        Takes a RawData request, returns RawData response from server.
        '''
        tries = 0
        self.make_socket()
        try:
            while tries < 1 + self.retries:
                self.socket.sendto(req_pkt.export(), self.remote_addr)
                try:
                    return RawData(self.socket.recv(512))
                except socket.timeout:
                    tries += 1
        finally:
            self.close_socket()

        raise Exception('External resolution timed out')

    def get(self, req_in):
        req_out = self._make_request(req_in.name, req_in.qtype, req_in.qclass)

        resp = self.exchange(req_out)
        if resp.flag_rcode != 0:
            raise Exception("Query failed with code %d" % resp.flag_rcode)
        else:
            return list(resp.records)

    def _make_request(self, domain, qtype=None, qclass=None):
        '''
        Create a Request object for exchange based on a given domain.
        '''
        self.appid += 1
        req = Request(qid=self.appid, qtype=qtype, qclass=qclass)
        req.name = domain
        req.flag_rd = True # Use recursion where available

        return req

class DummyDnsSource(DnsSource):
    '''
    Always use a given 'response' packet, instead of live query.
    '''
    def __init__(self, packet):
        DnsSource.__init__(self)
        self.packet = packet

    def _exchange_data(self, req_pkt):
        '''
        Return the predetermined packet.
        '''
        return self.packet

class MultiDNS(object):
    '''
    Not a source, but a utility class that simplifies requesting to
    multiple different servers on demand.
    '''

    def __init__(self):
        self.cache = {}

    def add(self, dnssource):
        '''
        Add a DnsSource object to collection.
        '''
        self.cache[dnssource.remote_addr] = dnssource

    def make(self, remote_addr):
        '''
        Create and return a DnsSource object. Does not register it.
        '''
        return DnsSource(remote=remote_addr)

    def get_source(self, remote_addr):
        '''
        Return a source for the remote address, creating if necessary.
        '''
        if not (remote_addr in self.cache):
            self.add(self.make(remote_addr))
        return self.cache[remote_addr]

    def get(self, domain_name, server_addr):
        '''
        Retrieve domain name info from a given server.
        '''
        return self.get_source(server_addr).get_domain_string(domain_name)
