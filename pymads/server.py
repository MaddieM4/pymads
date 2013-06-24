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

import socket
import sys

from pymads.consumer import Consumer
from pymads.errors import ErrorConverter
from pymads.extern import queue

DEFAULT_CONFIG = {
    'listen_host' : '0.0.0.0',
    'listen_port' : 53,
    'debug'  : False,
    'chains' : [],
    'queue_class' : queue.Queue,
    'own_consumer': True, # Set to False for multithread/extern consumer
}

class DnsServer(object):
    '''
    Serves DNS data based on the configuration you give it.
    '''

    def __init__(self, **kwargs):
        '''
        Use keyword arguments to override the defaults.

        See pymads.server.DEFAULT_CONFIG for more info.
        '''
        self.config  = dict(DEFAULT_CONFIG) # Clone
        self.config.update(kwargs) # Customize
        self.serving = True
        self.socket  = None
        self.guard   = ErrorConverter(['SERVFAIL'])
        self.queue   = self.config['queue_class']()
        self._default_consumer = Consumer(self)

    def __repr__(self):
        return '<pymads dns serving on %s:%d>' % (
            self.listen_host, self.listen_port
        )

    @property
    def listen_port(self):
        '''
        Port that the server will listen on.
        '''
        return self.config['listen_port']

    @listen_port.setter
    def listen_port(self, port):
        """
        Sets the port the server binds to.
        """
        self.config['listen_port'] = int(port)

    @property
    def listen_host(self):
        '''
        Host that the server will listen on.
        '''
        return self.config['listen_host']

    @listen_host.setter
    def listen_host(self, host):
        """
        Sets the host/ipaddress the server will bind to.
        """
        self.config['listen_host'] = int(host)

    @property
    def debug(self):
        '''
        Debug mode affects how the server deals with errors.

        In debug mode, lookup failures and error tracebacks will be printed.
        '''
        return self.config['debug']

    @debug.setter
    def debug(self, debug):
        """
        Sets whether we are in debug mode.
        """
        self.config['debug'] = bool(debug)

    def bind(self):
        """
        Bind socket (allows privelege dropping between bind and service).
        """
        if not self.socket:
            if isinstance(self.listen_host, tuple):
                host, flow, scope = self.listen_host
                self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self.socket.bind((host, self.listen_port, flow, scope))
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.bind((self.listen_host, self.listen_port))
            self.socket.settimeout(1)

    def serve(self):
        """
        Serves forever. Or at least until you call server.stop().
        """

        self.bind()
        udps = self.socket
        while self.serving:
            try:
                # max UDP DNS pkt size = 512
                req_pkt, src_addr = udps.recvfrom(512)
            except socket.error:
                continue

            self.queue.put((req_pkt, src_addr))
            if self.config['own_consumer']:
                self._default_consumer.consume()

    def stop(self):
        '''
        Stop a running server.
        '''
        self.serving = False
        if hasattr(self, 'socket'):
            self.socket.close()
        self.queue.join()

def die(msg):
    """
    Print message to stderr and crash.
    """
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

    path   = options['<source_path>']
    if path == '-':
        source_file = sys.stdin
    else:
        source_file = open(path)

    source = JSONSource(source_file)
    chain  = Chain([source])
    config['chains'] = [chain]

    server = DnsServer(**config)
    server.serve()

if __name__ == '__main__':
    serve_standalone(*sys.argv[1:])
