'''
    Unittests/Chemical/Proteins/peptide_list
    ________________________________________

    Test suite for peptide containers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import random
import unittest

from xldlib.chemical.proteins import peptide, peptide_list

# ITEMS
# -----

PEPTIDES = [
    peptide.Peptide('EIETEEK', 1, 0),
    {'sequence': 'EIETEEK', 'start': 1, 'id': 0},
    ['EIETEEK', 1, 0],
    ('EIETEEK', 1, 0),
]

SORTING = [
    peptide.Peptide('EIETEEK', 1, 0),
    peptide.Peptide('NLHLEEIFCSIK', 8, 0),
    peptide.Peptide('VQLDAYEPADCELYR', 20, 0),
    peptide.Peptide('DK', 35, 0),
    peptide.Peptide('AELK', 37, 0),
    peptide.Peptide('CAFK', 41, 0),
]

POSITIONS = [1, 8, 20, 35, 37, 41]


# CASES
# -----


class TestPeptides(unittest.TestCase):
    '''Test list additions and sorting for the `Peptides` container'''

    def test_items(self):
        '''Test `Peptide` item recognition from heterogeneous data'''

        peptides = peptide_list.Peptides()
        for item in PEPTIDES:
            peptides.append(item)
            self.assertIsInstance(peptides[0], peptide.Peptide)
            self.assertEquals(peptides[0], PEPTIDES[0])
            peptides.clear()

    def test_sorting(self):
        '''Test peptides are sorted sequentially by protein position'''

        peptides = peptide_list.Peptides()
        random.shuffle(SORTING)
        for item in SORTING:
            peptides.append(item)

        peptides.sort()
        self.assertEquals([i.start for i in peptides], POSITIONS)

# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(TestPeptides('test_items'))
    suite.addTest(TestPeptides('test_sorting'))
