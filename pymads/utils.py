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

import struct

try:
    bytes
except:
    bytes = str

def label2str(label):
    s = struct.pack("!B", len(label))
    s += label
    return s
    
def labels2str(labels):
    s = bytes()
    for label in labels:
        s += label2str(label)
    s += struct.pack("!B", 0)
    return s

def ipstr2int(ipstr):
    ip = 0
    i = 24
    for octet in ipstr.split("."):
        ip |= (int(octet) << i)
        i -= 8
    return ip

