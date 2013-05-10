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
from pymads.extern import ConfigParser
import optparse
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

    def serve(self):
        """Serves forever"""

        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.bind((self.listen_host, self.listen_port))
        #ns_resource_records, ar_resource_records = compute_name_server_resources(_name_servers)
        ns_resource_records = ar_resource_records = []
        while True:
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
                for chain in self.config['chains']:
                    rcode, an_records = chain.get(req)
                    resp = response.Response(req, rcode, an_records)
                    resp_pkt = str(resp)
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
                    raise Exception("query is not for our domain: %s" % ".".join(req.question))
            except:
                if req.qid:
                    if exception_rcode is None:
                        exception_rcode = 2
                    resp = response.Response(req, exception_rcode)
                    resp_pkt = str(resp)
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

    def die(self, msg):
        """Just a msg wrapper"""

        sys.stderr.write(msg)
        sys.exit(-1)


def main():

    usage = '%prog [options] [config_files]\n\nconfig_files = One or more config files, defaults to "pymads.conf"'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-p', '--port', dest='port', type=int, default=53,
        help='Port to run the DNS server on (default: 53)')
    parser.add_option('-i', '--ip', dest='ip', default='0.0.0.0',
        help='IP to bind ourselved on to (default: 0.0.0.0)')
    parser.add_option('-d', '--debug', dest='debug', default=False, action='store_true',
        help='Debug mode, this may impact performance since it has to flush on every query')
    (options, filenames) = parser.parse_args()

    config_files = {}
    if not filenames:
        filenames = ['pymads.conf']
    for f in filenames:
        if f in config_files:
            raise Exception("repeated configuration")
        config_files[f] = {}

    sys.stdout.write("%s starting on %s:%d\n" % (sys.argv[0], options.ip, options.port))
    dns = DnsServer(config_files=config_files, listen_port=options.port, listen_host=options.ip)
    dns.set_debug(options.debug)
    signal.signal(signal.SIGHUP, dns.reread)
    for config in config_files.values():
        sys.stdout.write("%s: serving for domain %s\n" % (sys.argv[0], ".".join(config['domain'])))
    sys.stdout.flush()
    sys.stderr.flush()
    dns.serve()

if __name__ == "__main__":
    sys.exit(main())

