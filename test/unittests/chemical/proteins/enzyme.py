'''
    Unittests/Chemical/Proteins/enzyme
    __________________________________

    Test suite for proteolytic enzyme cut specificity.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.chemical.proteins import enzyme

from ._data import SEQUENCES

# ITEMS
# -----


ENZYMES = [
    'Trypsin',
    'Lys-N',
]


# CASES
# -----


class EnzymeTest(unittest.TestCase):
    '''Test for enzymatic objects and cut specificity'''

    #     TESTS

    def test_cleavage(self):
        '''Test proteolytic cleavage of target sequences'''

        for index, sequence in enumerate(SEQUENCES):
            for name in ENZYMES:
                self._test_sequence(sequence, name)

    def test_lookup(self):
        '''Ensure protease lookups are name-specific'''

        self.assertTrue(enzyme.ProteolyticEnzyme())
        self.assertTrue(enzyme.ProteolyticEnzyme('Trypsin'))

        with self.assertRaises(KeyError):
            enzyme.ProteolyticEnzyme("Not an enzyme")

    #   NON-PUBLIC

    def _test_sequence(self, sequence, name):
        '''Test proteolytic cleavage of a target sequence'''

        protease = enzyme.ProteolyticEnzyme(name)
        while sequence:
            cut = protease.cut_peptide(sequence)

            # grab the start position relative to sequence
            start = cut.position
            if protease.enzyme.cterm:
                start -= 1
            if start > 0:
                self.assertIn(sequence[start], protease.enzyme.cut)
            sequence = cut.remaining

# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(EnzymeTest('test_cleavage'))
    suite.addTest(EnzymeTest('test_lookup'))
