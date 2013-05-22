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

from __future__ import print_function

import os
import sys
from pymads.extern import unittest

def main():
    loader = unittest.TestLoader()
    if len(sys.argv) > 1:
        tests = unittest.TestSuite()
        names = sys.argv[1:]
        for name in names:
            try:
                test = loader.loadTestsFromName('%s.%s' % (__package__, name))
            except AttributeError as ex:
                print("Error loading '%s': %s" % (name, ex))
                quit(1)
            tests.addTests(test)
    else:
        base_path = os.path.split(__file__)[0]
        tests = loader.discover(base_path)
    test_runner = unittest.runner.TextTestRunner()
    results = test_runner.run(tests)
    if not results.wasSuccessful():
        quit(1)

if __name__ == '__main__':
    main()
