'''
    Unittests/General/Sequence
    __________________________

    Test suite for sequence object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import defaultlist, extendable, functions, lookup, user


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    defaultlist.add_tests(suite)
    extendable.add_tests(suite)
    functions.add_tests(suite)
    lookup.add_tests(suite)
    user.add_tests(suite)
