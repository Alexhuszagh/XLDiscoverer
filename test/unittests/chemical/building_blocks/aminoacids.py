'''
    Unittests/Chemical/Building_Blocks/aminoacids
    _____________________________________________

    Unit tests for aminoacid lookups.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.chemical.building_blocks import aminoacids


# CASES
# -----


class AminoAcidTest(unittest.TestCase):
    '''Test aminoacid lookups'''

    def test_mixed_case(self):
        '''Test mixed-case lookups produce the same object'''

        lower = aminoacids.AMINOACIDS['a']
        upper = aminoacids.AMINOACIDS['A']

        self.assertEquals(id(lower), id(upper))
        self.assertEquals(lower, upper)

        assert 'a' in aminoacids.AMINOACIDS
        assert 'A' in aminoacids.AMINOACIDS


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(AminoAcidTest('test_mixed_case'))
