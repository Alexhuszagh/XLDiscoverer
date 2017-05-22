'''
    Unittests/Chemical/formula
    __________________________

    Unit tests for chemical formula parsers and molecule objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from xldlib.chemical import formula

# OBJECTS
# -------

Formula = namedlist("Formula", "string strict conditions")
Condition = namedlist("Condition", "formula mass")

# ITEMS
# -----

FORMULAS = [
    Formula("C2", False, [
        Condition("C2", 24.0),
        Condition("C4", 48.0),
        ]),
    Formula("Hex", False, [
        Condition('O5 C6 H10', 162.05282347),
        Condition('O10 C12 H20', 324.10564694),
        ]),
    Formula("HexNAc", False, [
        Condition('O5 N1 C8 H13', 203.0793725725),
        Condition('O10 N2 C16 H26', 406.158745145),
        ])
]

PEPTIDES = [
    Formula("SAMPLER", False, [
        Condition('S1 O11 N10 C33 H58', 802.4007235438),
        Condition('S2 O22 N20 C66 H116', 1604.8014470876),
        ]),
    Formula("SAMPLZR", True, [
        Condition('S1 O11 N10 C33 H58', 802.4007235438),
        Condition('S2 O22 N20 C66 H116', 1604.8014470876),
        ]),
    Formula("SAMXXX", True, [
        Condition('S1 O5 N3 C38 H30', 640.1906168286),
        Condition('S2 O10 N6 C76 H60', 1280.3812336572),
        ])
]

# CASES
# -----


class AtomTest(unittest.TestCase):
    '''Test for the Atom defaultdict with `__mul__` properties'''

    def test_mul(self):
        '''Test multiplication of the Atom'''

        atom = formula.Atom({-1: 5})
        self.assertEquals(atom * 5, {-1: 25})


class MoleculeTest(unittest.TestCase):
    '''Tests for chemical formula parsing and molecule properties'''

    #     TESTS

    def test_formulas(self):
        '''Test parsing of chemical formulas'''

        for item in FORMULAS:
            self._test_molecule('formula', item)

    def test_peptide(self):
        '''Test parsing of aminoacid sequences'''

        for item in PEPTIDES:
            for strict in (False, True):
                self._test_molecule('peptide', item, strict)

    def test_properties(self):
        '''Test Molecules are re-exported to string'''

    #   NON-PUBLIC

    def _test_molecule(self, kwd, item, strict=False):
        '''Test a parsing condition'''

        if item.strict and strict:
            self._test_error(kwd, item, strict)
        else:
            self._test_parsing(kwd, item, strict)

    def _test_error(self, kwd, item, strict):
        '''Test non-strict inputs raise a KeyError'''

        with self.assertRaises(KeyError):
            formula.Molecule(strict=strict, **{kwd: item.string})

    def _test_parsing(self, kwd, item, strict):
        '''Test formula produces expected output'''

        one = formula.Molecule(strict=strict, **{kwd: item.string})
        self.assertEquals(one.tostr(), item.conditions[0].formula)
        self.assertAlmostEquals(one.mass, item.conditions[0].mass, 5)

        # test mul
        two = one * 2
        self.assertEquals(two.tostr(), item.conditions[1].formula)
        self.assertAlmostEquals(two.mass, item.conditions[1].mass, 5)

        # check update with -1 count
        two.update_formula(count=-1, **{kwd: item.string})
        self.assertEquals(two.tostr(), item.conditions[0].formula)
        self.assertAlmostEquals(two.mass, item.conditions[0].mass, 5)

        # test imul
        one *= 2
        self.assertEquals(one.tostr(), item.conditions[1].formula)
        self.assertAlmostEquals(one.mass, item.conditions[1].mass, 5)

        # assert same as defining counts
        two = formula.Molecule(count=2, strict=strict, **{kwd: item.string})
        self.assertEquals(two.tostr(), item.conditions[1].formula)
        self.assertAlmostEquals(two.mass, item.conditions[1].mass, 5)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(AtomTest('test_mul'))
    suite.addTest(MoleculeTest('test_formulas'))
    suite.addTest(MoleculeTest('test_peptide'))
    suite.addTest(MoleculeTest('test_properties'))
