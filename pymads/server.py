#!/usr/bin/env python
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
from __future__ import unicode_literals

import traceback
import signal
import socket
import struct
import sys

from pymads import utils, request, response
from pymads.errors import DnsError, ErrorConverter

default_config = {
    'listen_host' : '0.0.0.0',
    'listen_port' : 53,
    'debug' : False,
    'chains' : [],
}

class DnsServer(object):

    def __init__(self, **kwargs):
        self.config  = dict(default_config) # Clone
        self.config.update(kwargs) # Customize
        self.serving = True
        self.socket  = None
        self.guard   = ErrorConverter(['SERVFAIL'])

    def __repr__(self):
        return '<pymads dns serving on %s:%d>' % (self.listen_host, self.listen_port)

    @property
    def listen_port(self):
        return self.config['listen_port']

    @listen_port.setter
    def listen_port(self, port):
        """Sets the port who should bind ourselves to"""
        self.config['listen_port'] = int(port)

    @property
    def listen_host(self):
        return self.config['listen_host']

    @listen_host.setter
    def listen_host(self, host):
        """Sets the host/ipaddress we should bind ourselves to"""
        self.config['listen_host'] = int(host)

    @property
    def debug(self):
        return self.config['debug']

    @debug.setter
    def debug(self, debug):
        """Sets whether we are in debug mode"""
        self.config['debug'] = bool(debug)

    def bind(self):
        """Bind socket (allows privelege dropping between bind and service)"""
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.listen_host, self.listen_port))
            self.socket.settimeout(1)

    def serve(self):
        """Serves forever"""

        self.bind()
        udps = self.socket
        #ns_resource_records, ar_resource_records = compute_name_server_resources(_name_servers)
        ns_resource_records = ar_resource_records = []
        while self.serving:
            req = None

            try:
                req_pkt, src_addr = udps.recvfrom(512)   # max UDP DNS pkt size
            except socket.error:
                continue

            try:
                with self.guard.quiet(not self.debug):
                    req = request.parse(req_pkt, src_addr)
                    resp_pkt = self.serve_one(req)

            except DnsError as e:
                if not req:
                    # Attempt to salvage a little information
                    if len(req_pkt) < 2:
                        continue
                    qid = struct.unpack(b'!H', req_pkt[:2])[0]
                    req = request.Request(qid, [], 1, 1, src_addr)

                resp = response.Response(req, e.code)
                resp_pkt = resp.export()

            udps.sendto(resp_pkt, src_addr)

    def serve_one(self, req):
        for chain in self.config['chains']:
            records = chain.get(req.name)
            if records:
                if self.debug:
                    sys.stdout.write('Found %r' % req)
                    sys.stdout.flush()
                resp = response.Response(req, 0, records)
                return resp.export()
        # No records found
        if self.debug:
            sys.stderr.write('Unknown %r' % req)
            sys.stderr.flush()
        raise DnsError('NXDOMAIN', "query is not for our domain: %r" % req)

    def compute_name_server_resources(self, name_servers):
        ns = []
        ar = []
        for name_server, ip, ttl in name_servers:
            ns.append({'qtype':2, 'qclass':1, 'ttl':ttl, 'rdata':utils.labels2str(name_server)})
            ar.append({'qtype':1, 'qclass':1, 'ttl':ttl, 'rdata':struct.pack("!I", ip)})
        return ns, ar

    def stop(self):
        self.serving = False
        if hasattr(self, 'socket'):
            self.socket.close()

    def die(self, msg):
        """Just a msg wrapper"""

        sys.stderr.write(msg)
        sys.exit(-1)

def serve_standalone(*args):
    '''
    usage: server.py [options] <source_path>

    Source path should be the location of a JSON file, or '-' for STDIN.

    options:
        -P, --listen-port PORT   Port to listen on         [default: 53]
        -H, --listen-host HOST   Host address to listen on [default: 0.0.0.0]

        -v --verbose             Verbose output
        -d --debug               Debug mode
        -h --help                Show help
        --version                Show version and exit
    '''
    from docopt import docopt

    from pymads.chain import Chain
    from pymads.sources.json import JSONSource

    options = docopt(serve_standalone.__doc__, argv=list(args), version='0.1.0')

    config  = {}
    config['listen_port'] = int(options['--listen-port'])
    config['listen_host'] = options['--listen-host']
    config['debug']       = options['--debug']

    path    = options['<source_path>']
    if path == '-':
        fp = sys.STDIN
    else:
        fp = open(path)

    source = JSONSource(fp)
    chain  = Chain([source])
    config['chains'] = [chain]

    server = DnsServer(**config)
    server.serve()

if __name__ == '__main__':
    serve_standalone(*sys.argv[1:])
