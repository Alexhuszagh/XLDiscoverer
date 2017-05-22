'''
    Unittests/Qt/memo
    _________________

    Test suite for Qt memos, which record (and keep alive) important
    widget instances bound to the QApplication.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from PySide import QtCore

from xldlib.onstart.main import APP
from xldlib.qt import memo

# OBJECTS
# -------


@memo.view
class QtObject(QtCore.QObject):
    '''Generic Qt class for testing'''

    def __init__(self, *args, **kwds):
        '''Initializer since init is not called by default for QObject'''
        super(QtObject, self).__init__(*args, **kwds)


@memo.thread
class QtThread(QtCore.QThread):
    '''Generic Qt thread class for testing'''

    def __init__(self, *args, **kwds):
        '''Initializer since init is not called by default for QThread'''
        super(QtThread, self).__init__(*args, **kwds)



# CASES
# -----


class MemoTest(unittest.TestCase):
    '''Tests for memoizing widgets with `app.views` and `app.threads`'''

    def test_view(self):
        '''Test adding items to the view memo'''

        self.assertNotIn('QtObject', APP.views)

        inst = QtObject()
        self.assertIn('QtObject', APP.views)
        self.assertIs(inst, APP.views['QtObject'])

    def test_view_reference(self):
        '''Test objects added in views are strongly referenced'''

        self.assertIn('QtObject', APP.views)

    def test_threads(self):
        '''Test adding items to the threads memo'''

        self.assertNotIn('QtThread', APP.threads)

        inst = QtThread()
        self.assertIn('QtThread', APP.threads)
        self.assertIs(inst, APP.threads['QtThread'])

    def test_threads_reference(self):
        '''Test objects added in threads are weakly referenced'''

        self.assertNotIn('QtThread', APP.threads)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(MemoTest('test_view'))
    suite.addTest(MemoTest('test_view_reference'))
    suite.addTest(MemoTest('test_threads'))
    suite.addTest(MemoTest('test_threads_reference'))
