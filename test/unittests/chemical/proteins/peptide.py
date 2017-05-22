'''
    Chemical/Proteins/peptide
    _________________________

    Tests for peptide definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.chemical.proteins.peptide import Peptide


# CASES
# ------


class PeptideTest(unittest.TestCase):
    '''Test peptide object behavior'''

    def test_merge(self):
        '''Test merging peptides'''

        first = Peptide('MK', 1, 'P02769', "ALBU_BOVIN", 0)
        second = Peptide('WVTFISLLLLFSSAYSR', 3, 'P02769', "ALBU_BOVIN", 0)
        first.merge(second)
        self.assertEquals(first.missed_cleavages, 1)
        self.assertEquals(first.sequence, 'MKWVTFISLLLLFSSAYSR')


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(PeptideTest('test_merge'))
