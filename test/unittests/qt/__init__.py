'''
    Unittests/Qt
    ____________

    Test suite for Qt definitions, which provide the core of
    XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import memo, objects, resources

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    memo.add_tests(suite)
    objects.add_tests(suite)
    resources.add_tests(suite)
