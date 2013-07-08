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
from persei import RawData, RawDataDecorator
from pymads.errors import DnsError

@RawDataDecorator()
def label2str(label):
    '''
    Convert a single label component into the length + content form.

    'google' -> '{6}google'
    '''
    packed = RawData(struct.pack("!B", len(label)))
    packed += RawData(label)
    return packed

def labels2str(labels):
    '''
    Turn a label array into a terminated serialized string.

    ['google', 'com'] -> '{6}google{3}com{0}'
    '''
    packed = RawData()
    for label in labels:
        packed += RawData(label2str(label))
    packed += RawData(struct.pack("!B", 0))
    return packed

def str2labels(source, offset=0):
    '''
    Deserializes a string into a label array, based on a buffer.

    The awkward API is because DNS supports compression-by-reference, where
    you say "fetch this data from another part of the packet." This lets
    packet creators shave off redundant bytes, usually by setting record
    labels to point to the question data.

    For pymads to be able to handle this feature when interacting with
    other computers, the str2labels function has to be provided the whole
    packet, and the offset for the label string you want deserialized. It
    also gives you the number of bytes consumed, to help you keep parsing
    the packet.

    packet, 18 -> (12, ['google','com'])
    '''
    labels = []
    source = RawData(source)
    while True:
        length, = struct.unpack('!B', source[offset:offset+1].export())
        if length & 0xc0:
            pointer, = struct.unpack('!H', source[offset:offset+2].export())
            pointer = pointer & 0x3fff # 0xffff - 0xc000, bitmask for pointer
            if pointer > len(source):
                raise DnsError('FORMERR', 'Bad pointer')
            return offset+2, labels + str2labels(source, pointer)[1]
        offset += 1
        if length == 0:
            break
        label = source[offset:offset+length]
        offset += length
        labels.append(label)
    return offset, labels
