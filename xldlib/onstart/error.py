'''
    Onstart/error
    _____________

    Error messages on loading XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore, QtGui

# ERRORS
# ------


class ImportErrorDialog(QtGui.QMessageBox):
    '''`QMessageBox` with bound error for a a missing import'''

    def __init__(self, error, parent=None):
        '''
        Args:
            error (str):    text to warn user about missing import
            parent (QObject, None):     Qt parent
        '''
        super(ImportErrorDialog, self).__init__(parent)

        self.setWindowTitle('Import Error')
        self.setTextFormat(QtCore.Qt.RichText)
        self.setText(error)
