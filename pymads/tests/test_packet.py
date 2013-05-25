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

from pymads.extern import unittest
from pymads.packet import Packet

class TestPacket(unittest.TestCase):
    def test_flag_set(self):
        packet = Packet()
        self.assertEquals(packet.flags, 0)

        for width in range(1,4):
            size = sum(2**i for i in range(width))
            for position in range(16-width):
                for value in range(size+1):
                    packet.setflag(position, size, value)
                    self.assertEqual(
                        packet.getflag(position, size),
                        value
                    )

    def test_flag_rcode(self):
        packet = Packet()
        packet.flag_rcode = 15
        self.assertEquals(
            packet.flags,
            15
        )

    def do_test_pack_cycle(self, p_orig):
        p_clone = Packet()
        p_clone.unpack(p_orig.pack())
        self.assertEquals(p_orig.pack(), p_clone.pack())

    def test_cycle_request(self):
        from pymads.request import Request

        req = Request(31, [], 'AAAA')
        req.name = "example.com"

        self.do_test_pack_cycle(req)
