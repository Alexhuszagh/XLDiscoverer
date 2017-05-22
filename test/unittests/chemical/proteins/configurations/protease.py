'''
    Unittests/Chemical/Proteins/Configurations/protease
    ___________________________________________________

    Test suite for proteolytic enzyme configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from xldlib.chemical.proteins.configurations import protease
from xldlib.definitions import re

# OBJECTS
# -------

Test = namedlist("Test", "sequence position")


# ITEMS
# -----

PROTEASES = [
    ('Trypsin', ['K', 'R'], ['P'], protease.TERMINI['C']),
    ('Lys-C', ['K'], [], protease.TERMINI['C']),
    ('Lys-N', ['K'], [], protease.TERMINI['N']),
    ('Fake-TrypsinN', ['K', 'R'], ['P'], protease.TERMINI['N']),
]

TESTS = [
    Test("MKWVTF", [1, 1, 0, 0]),
    Test("PKLKPDPNTLCDEFK", [1, 1, 0, 2]),
    Test("CCTESLVNRRPCFSALT", [8, None, None, 7]),
    Test("CCTESLVNRPCFSALT", [None, None, None, 7]),
]


# CASES
# -----


class ProteaseTest(unittest.TestCase):
    '''tests for the protease object'''

    #     TESTS

    def test_proteases(self):
        '''Test the protease properties'''

        for index, item in enumerate(PROTEASES):
            enzyme = protease.Protease(*item)
            for test in TESTS:
                position = test.position[index]
                self._test_protease(enzyme, test.sequence, position)

    #   NON-PUBLIC

    def _test_protease(self, enzyme, sequence, position):
        '''Test properties of a singular protease'''

        match = re.search(enzyme.cut_regex, sequence)
        if position is None:
            self.assertIsNone(match)
        else:
            self.assertEquals(match.start(), position)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ProteaseTest('test_proteases'))
