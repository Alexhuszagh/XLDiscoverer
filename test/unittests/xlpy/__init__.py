'''
    Unittests/XlPy
    ______________

    Test suite for the XL Discoverer modules.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import matched, tools


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    matched.add_tests(suite)
    tools.add_tests(suite)
