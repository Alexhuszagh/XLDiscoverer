'''
    Unittests/Qt/Objects/Threads/base
    _________________________________

    Test suite for Qt thread object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.qt.objects import threads


# CASES
# -----


class BaseThreadTest(unittest.TestCase):
    '''Tests base QThread class'''

    def setUp(self):
        '''Set up unittests'''

        self.thread = threads.BaseThread()

    def test_memo(self):
        '''Test BaseThread initialization is memoized'''

        self.assertIn('BaseThread', self.thread.app.threads)

    def test_run(self):
        '''Test BaseThread raises an error for the standard implementation'''

        with self.assertRaises(NotImplementedError):
            self.thread.run()

    def tearDown(self):
        '''Tear down unittests'''

        del self.thread

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    BaseThreadTest('test_memo')
    BaseThreadTest('test_run')
