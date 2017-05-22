'''
    Unittests/Exception
    ___________________

    Unit tests for exception class definitions and exception handlers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import classes, grammar, tools

# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    classes.add_tests(suite)
    grammar.add_tests(suite)
    tools.add_tests(suite)
