'''
    Unittests/Gui/args
    __________________

    Ensure args are passed during initialization.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import importlib
import sys
import unittest

from xldlib.onstart import args


# CASES
# -----


class ArgTest(unittest.TestCase):
    '''Test argument parsing'''

    def test_args(self):
        '''Test argument parsing and then flag generation'''

        old = sys.argv[:]
        sys.argv[:] = ['xldiscoverer.pyw', '-l', 'DEBUG', '-d']

        new = importlib.reload(args)
        self.assertEquals(new.LOG, 'DEBUG')
        self.assertTrue(new.DEBUG)

        sys.argv[:] = old


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ArgTest('test_args'))
