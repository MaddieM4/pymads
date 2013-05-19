#!/usr/bin/env python

# Copyright (c) 2009 Tom Pinckney
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#     OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#     NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#     HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#     WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#     OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import

import traceback
import signal
import socket
import struct
import sys

from pymads import utils, request, response
from pymads.errors import *

default_config = {
    'listen_host' : '0.0.0.0',
    'listen_port' : 53,
    'debug' : False,
    'chains' : [],
}

class DnsServer(object):

    def __init__(self, **kwargs):
        self.config = dict(default_config) # Clone
        self.config.update(kwargs) # Customize
        self.serving = True
        self.socket = None

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
            try:
                req_pkt, src_addr = udps.recvfrom(512)   # max UDP DNS pkt size
            except socket.error:
                continue
            try:
                exception_rcode = None
                try:
                    req = request.parse(req_pkt, src_addr)
                except:
                    exception_rcode = 1
                    raise Exception("could not parse query")

                found = False
                for chain in self.config['chains']:
                    an_records = list(chain.get(req.name))
                    if an_records:
                        resp = response.Response(req, 0, an_records)
                        resp_pkt = resp.export()
                        found = True
                        if self.debug:
                            sys.stdout.write('Found %r' % req)
                            sys.stdout.flush()
                        break
                if not found:
                    if self.debug:
                        sys.stderr.write('Unknown %r' % req)
                        sys.stderr.flush()
                    exception_rcode = 3
                    raise Exception("query is not for our domain: %r" % req)
            except:
                traceback.print_exc(file=sys.stdout)
                if req.qid:
                    if exception_rcode is None:
                        exception_rcode = 2
                    resp = response.Response(req, exception_rcode)
                    resp_pkt = resp.export()
                else:
                    continue
            udps.sendto(resp_pkt, src_addr)

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
