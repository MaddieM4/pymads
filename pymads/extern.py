import sys
if (2, 7) <= sys.version_info[:2] < (3, 0) or sys.version_info >= (3, 2):
    import unittest
else:
    import unittest2 as unittest

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser
