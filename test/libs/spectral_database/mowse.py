


# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(path)


class TestMowse(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
