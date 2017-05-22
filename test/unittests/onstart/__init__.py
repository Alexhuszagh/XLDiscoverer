'''
    Unittests/Gui
    _____________

    Unittests for elements which start XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import app, args, check_imports, error

# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    app.add_tests(suite)
    args.add_tests(suite)
    check_imports.add_tests(suite)
    error.add_tests(suite)
