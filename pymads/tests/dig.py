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

import subprocess

def dig(hostname, test_host='localhost', test_port=53000):
    sp = subprocess.Popen(
        ['dig', '@' + test_host, '-p%d' % test_port, hostname, 'ANY'],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        universal_newlines = True
    )
    return sp.communicate()[0] # STDOUT
