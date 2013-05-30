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
from pymads.errors import DnsError

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

def str2labels(source, offset=0):
    '''
    Returns (length, ['label','list'])
    '''
    labels = []
    while True:
        length, = struct.unpack('!B', source[offset:offset+1])
        if length & 0xc0:
            pointer, = struct.unpack('!H', source[offset:offset+2])
            pointer = pointer & (0xff-0xc0)
            if pointer > len(source):
                raise DnsError('FORMERR', 'Bad pointer')
            return offset+2, str2labels(source, pointer)[1]
        offset += 1
        if length == 0:
            break
        label = source[offset:offset+length]
        offset += length
        labels.append(label)
    return offset, labels

def byteify(obj):
    try:
        return bytes(obj, 'utf-8')
    except:
        return str(obj)

def stringify(obj):
    if hasattr(obj, 'decode'):
        return obj.decode()
    else:
        return str(obj)
