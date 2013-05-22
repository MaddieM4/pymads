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

import socket
import random

from pymads.utils import *

class Filter(object):
    def __init__(self, netmask):
        self._cache = {}
        if netmask[:2] == '0x':
            base = 16
            netmask = netmask[2:]
        else:
            base = 10
        self._netmask = int(netmask,base)

    def filter(self, query, domain, qtype, qclass, src_addr, an_resource_records):
        if qtype != 1 or len(an_resource_records) < 2:
            return an_resource_records
        src_ip = ipstr2int(src_addr[0])
        result = []    
        if self._netmask:
            key = str(src_ip & self._netmask) + "_" + query
            resource = None
            if key in self._cache:
                resource = self._cache[key]
                if resource in an_resource_records:
                    result.append(resource)
                    rest = [x for x in an_resource_records if x != resource]
                    result.extend(rest)
                else:
                    del self._cache[key]
        if not result:
            result = an_resource_records[:]
            random.shuffle(result)
            if self._netmask:
                if key not in self._cache:
                    self._cache[key] = result[0]
        return result
