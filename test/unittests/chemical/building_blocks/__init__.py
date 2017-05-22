'''
    Unittests/Chemical/Building_Blocks
    __________________________________

    Unit tests for chemical building blocks.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from . import aminoacids


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    aminoacids.add_tests(suite)
