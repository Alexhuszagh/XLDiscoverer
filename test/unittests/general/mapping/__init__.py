'''
    Unittests/General/Mapping
    _________________________

    Test suite for mapping object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import (frozen, functions, hashable, ordered,
               recursive, reverse, serialize, table)

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    frozen.add_tests(suite)
    functions.add_tests(suite)
    hashable.add_tests(suite)
    ordered.add_tests(suite)
    recursive.add_tests(suite)
    reverse.add_tests(suite)
    serialize.add_tests(suite)
    table.add_tests(suite)
