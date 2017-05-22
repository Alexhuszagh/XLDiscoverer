'''
    Unittests/Gui/error
    ___________________

    Unittests for a missing import errror dialog.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.onstart import error


# CASES
# -----


class ErrorDialogTest(unittest.TestCase):
    '''Test error dialog with proper text formatting'''

    def test_dialog(self):
        '''Test dialog construction'''

        dialog = error.ImportErrorDialog('Some text')
        dialog.show()
        self.assertEquals(dialog.isVisible(), True)

        dialog.hide()
        dialog.deleteLater()


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ErrorDialogTest('test_dialog'))
