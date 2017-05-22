'''
    Unittests/Chemical
    __________________

    Unit tests for chemical object definitions and resources.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import building_blocks, formula, proteins


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    building_blocks.add_tests(suite)
    formula.add_tests(suite)
    proteins.add_tests(suite)
