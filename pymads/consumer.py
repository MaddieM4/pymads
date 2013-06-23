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
import sys

from pymads import request
from pymads.errors import DnsError
import traceback

class Consumer(object):
    '''
    Class for consuming and processing requests from server queues.
    '''
    def __init__(self, server, timeout=0.1):
        self.server  = server
        self.timeout = timeout

    @property
    def queue(self):
        '''
        Convenience access: server queue.
        '''
        return self.server.queue

    @property
    def socket(self):
        '''
        Convenience access: server socket.
        '''
        return self.server.socket

    @property
    def serving(self):
        '''
        Convenience access: is server running?
        '''
        return self.server.serving

    @property
    def debug(self):
        '''
        Convenience access: is server in debug mode?
        '''
        return self.server.debug

    @property
    def guard(self):
        '''
        Convenience access: server error guard.
        '''
        return self.server.guard

    def listen(self):
        '''
        Loop for serving data.
        '''
        while self.serving:
            self.consume()

    def consume(self):
        '''
        Consume and serve one item from the queue.
        '''
        try:
            packet, source = self.queue.get(timeout = self.timeout)
        except:
            return

        try:
            with self.guard.quiet(not self.debug):
                req = request.Request()
                req.unpack(packet)
                resp_pkt = self.make_response(req)

        except DnsError as exc:
            try:
                resp = req.respond(exc.code)
                resp_pkt = resp.pack()
            except Exception: # Shit has completely hit the fan
                self.queue.task_done()
                traceback.print_exc()
                raise

        self.socket.sendto(resp_pkt, source)
        self.queue.task_done()

    def make_response(self, req):
        '''
        Process and respond to a request packet.
        '''
        for chain in self.server.config['chains']:
            records = chain.get(req.name)
            if records:
                if self.debug:
                    sys.stdout.write('Found %r' % req)
                    sys.stdout.flush()
                resp = req.respond(0, records)
                return resp.pack()
        # No records found
        if self.debug:
            sys.stderr.write('Unknown %r' % req)
            sys.stderr.flush()
        raise DnsError('NXDOMAIN', "query is not for our domain: %r" % req)
