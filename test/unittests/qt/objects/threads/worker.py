'''
    Unittests/Qt/Objects/Threads/worker
    ___________________________________

    Test suite for a worker Qt thread which executes a bound function
    within the thread loop.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.qt.objects import threads


# HELPERS
# -------


def raise_error():
    '''Raise an AttributeError to test thread execution'''

    raise AttributeError


# CASES
# -----


class BaseThreadTest(unittest.TestCase):
    '''Tests base QThread class'''

    def test_noerror(self):
        '''Test worker thread execution without an error'''

        self.thread = threads.WorkerThread(lambda: 1)
        self.thread.start()
        self.thread.wait()


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(BaseThreadTest('test_noerror'))
