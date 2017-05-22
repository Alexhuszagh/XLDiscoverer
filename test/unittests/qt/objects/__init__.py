'''
    Unittests/Qt/Objects
    ____________________

    Test suite for Qt objects definitions, which provide the core of
    XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import base, threads, views, window

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    base.add_tests(suite)
    threads.add_tests(suite)
    views.add_tests(suite)
    window.add_tests(suite)
