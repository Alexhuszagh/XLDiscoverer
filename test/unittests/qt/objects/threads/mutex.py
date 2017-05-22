'''
    Unittests/Qt/Objects/Threads/mutex
    __________________________________

    Test suite for the QMutex with context manager.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from PySide import QtCore

from xldlib.qt.objects.threads import mutex

# CASES
# -----

class MutexTest(unittest.TestCase):
    '''Tests lock/unlock state for QMutex'''

    def test_context(self):
        '''Test the context manager for the mutex'''

        mymutex = mutex.ContextMutex()
        self.assertTrue(mymutex.tryLock())
        mymutex.unlock()

        with mymutex:
            self.assertFalse(mymutex.tryLock())

        self.assertTrue(mymutex.tryLock())
        mymutex.unlock()

    def test_recursive(self):
        '''Test that multiple lock calls can be made for a recursive Mutex'''

        mymutex = mutex.ContextMutex(QtCore.QMutex.Recursive)
        with mymutex:
            with mymutex:
                pass


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(MutexTest('test_context'))
    suite.addTest(MutexTest('test_recursive'))
