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
from pymads.request import Request
from pymads.response import Response

class DnsSource(object):
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

        if '.' in local[0]:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.socket.bind(self.local_addr)
        self.socket.settimeout(1)

    def exchange(self, request):
        '''
        Return a Response object from remote.
        '''
        req_pkt = request.pack()
        tries = 0
        resp_pkt = ''

        while tries < 1 + self.retries:
            self.socket.sendto(req_pkt, self.remote_addr)
            try:
                resp_pkt = self.socket.recv(512)
                break
            except socket.timeout:
                tries += 1

        if resp_pkt == '':
            raise Exception('External resolution timed out')

        resp = Response()
        resp.unpack(resp_pkt)
        return resp

    def get(self, domain):
        self.appid += 1
        req = Request(self.appid)
        req.name = domain
        req.flag_rd = True # Use recursion where available

        resp = self.exchange(req)
        if resp.flag_rcode != 0:
            raise Exception("Query failed with code %d" % resp.flag_rcode)
        else:
            return set(resp.records)
