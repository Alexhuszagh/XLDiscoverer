'''
    Unittests/Chemical/Proteins/sequence_tools
    __________________________________________

    Unit tests for utilities for protein sequences.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from collections import Counter

from xldlib.chemical import proteins
from xldlib.chemical.proteins import sequence_tools
from xldlib.definitions import ZIP

from ._data import REVERSED, SEQUENCES

# ITEMS
# -----

PEPTIDES = [
    (('MK', 1, 0), ('LVVSTQTALA', 598, 0)),
    (('MVK', 1, 0), ('E', 333, 0)),
]


# CASES
# -----


class SequenceToolsTest(unittest.TestCase):
    '''Tests for processing protein sequences'''

    #     TESTS

    def test_decoys(self):
        '''Test decoy creation'''

        for sequence, reverse in ZIP(SEQUENCES, REVERSED):
            self.assertEquals(reverse, sequence_tools.make_decoy(sequence))
            shuffled = sequence_tools.make_decoy(sequence, 1)
            self.assertEquals(Counter(sequence), Counter(shuffled))

    def test_cleavage(self):
        '''Test protein cleavage into a peptide list'''

        enzyme = proteins.ProteolyticEnzyme('Trypsin')
        for sequence, (first, last) in ZIP(SEQUENCES, PEPTIDES):
            peptides = sequence_tools.cut_sequence(sequence, enzyme, False)
            peptides = list(peptides)
            self.assertEquals(peptides[0], first)
            self.assertEquals(peptides[-1], last)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(SequenceToolsTest('test_decoys'))
    suite.addTest(SequenceToolsTest('test_cleavage'))
