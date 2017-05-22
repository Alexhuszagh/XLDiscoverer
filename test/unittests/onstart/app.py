'''
    Unittests/Gui/error
    ___________________

    Unittests for custom QApplication object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from PySide import QtGui

from xldlib.onstart import app


# OBJECTS
# -------


class SplashWindow(object):
    '''Empty definition for an object'''


class BackgroundThread(object):
    '''Empty definition for a thread'''


# CASES
# -----


class AppTest(unittest.TestCase):
    '''Test QApplication definitions'''

    def test_application(self):
        '''Test application identifier'''

        self.assertIsInstance(QtGui.QApplication.instance(), app.App)

    def test_properties(self):
        '''Test application properties to memoize and fetch virws/threads'''

        app = QtGui.QApplication.instance()
        app.views['SplashWindow'] = SplashWindow()
        self.assertIsInstance(app.splashwindow, SplashWindow)

        app.threads['BackgroundThread'] = weakly = BackgroundThread()
        self.assertIsInstance(app.backgroundthread, BackgroundThread)

        del weakly
        with self.assertRaises(KeyError):
            # threads are weakly held
            app.backgroundthread


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(AppTest('test_application'))
    suite.addTest(AppTest('test_properties'))
