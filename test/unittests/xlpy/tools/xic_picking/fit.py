'''
    Unittests/XlPy/Tools/Xic_Picking/fit
    ____________________________________

    Test suite for XIC peak picking fitting and selection.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.xlpy.tools.xic_picking import fit


# CASES
# -----


class SelectionTest(unittest.TestCase):
    '''Test for peak selection'''

    def test_intersection(self):
        '''Test peak intersection for proper peak selection'''

        result = fit._intersection([(0, {'4'}), (1, {'4', '3', '5'})])
        self.assertEquals(result, {'4'})


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(SelectionTest('test_intersection'))
