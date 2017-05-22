'''
    Chemical/Proteins/protein
    _________________________

    Tests for protein definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import unittest

from collections import Counter

from xldlib.chemical.proteins import protein
from xldlib.definitions import ZIP

from ._data import LENGTHS, MOLECULAR_WEIGHTS, SEQUENCES


# ITEMS
# -----

PEPTIDES = [
    ('MKWVTFISLLLLFSSAYSR', 'LVVSTQTALA'),
    ('MVKVGVNGFGR', 'VVDLMVHMASKE'),
]


# CASES
# -----


class ProteinTest(unittest.TestCase):
    '''Test protein object behavior'''

    #     TESTS

    def test_properties(self):
        '''Test protein object properties'''

        for length, mw, sequence in ZIP(LENGTHS, MOLECULAR_WEIGHTS, SEQUENCES):
            inst = protein.Protein(sequence, 'test')
            self.assertEquals(inst.length, length)
            self.assertAlmostEquals(inst.mw, mw, 5)

    def test_sequencing(self):
        '''Test decoy creation'''

        for sequence, (first, last) in ZIP(SEQUENCES, PEPTIDES):
            inst = protein.Protein(sequence, 'test')
            inst.sequencing_peptides('Trypsin')

            self.assertEquals(inst.peptides[0].sequence, first)
            self.assertEquals(inst.peptides[-1].sequence, last)

    def test_decoys(self):
        '''Test decoy creation'''

        for sequence in SEQUENCES:
            inst = protein.Protein(sequence, 'test')
            self._test_reversed(copy.deepcopy(inst))
            self._test_shuffled(copy.deepcopy(inst))

    #   NON-PUBLIC

    def _test_reversed(self, inst):
        '''Test a reversed decoy with the instance of Protein'''

        reverse = inst.decoy()
        self.assertEquals(reverse.id, 'decoy')
        self.assertNotEquals(reverse, inst)
        self.assertEquals(inst.sequence, reverse.sequence[::-1])

        inst.decoy(in_place=True)
        self.assertEquals(reverse, inst)

    def _test_shuffled(self, inst):
        '''Test shuffled decoy with the instance of Protein'''

        reverse = inst.decoy('shuffled')
        self.assertEquals(reverse.id, 'decoy')
        self.assertNotEquals(reverse, inst)
        self.assertEquals(Counter(inst.sequence), Counter(reverse.sequence))

        inst.decoy('shuffled', in_place=True)
        self.assertEquals(reverse, inst)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ProteinTest('test_properties'))
    suite.addTest(ProteinTest('test_sequencing'))
    suite.addTest(ProteinTest('test_decoys'))
