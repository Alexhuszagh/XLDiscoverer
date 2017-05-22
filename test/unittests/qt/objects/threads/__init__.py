'''
    Unittests/Qt/Objects/Threads
    ____________________________

    Test suite for custom threads.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import background, base, mutex, worker


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    background.add_tests(suite)
    base.add_tests(suite)
    mutex.add_tests(suite)
    worker.add_tests(suite)
