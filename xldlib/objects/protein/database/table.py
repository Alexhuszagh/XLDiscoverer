'''
    Objects/Protein/database/table
    ______________________________

    Generalized model definitions for QTableViews.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore

from xldlib.qt.objects import base


# MODELS
# ------


class QTableModelItem(base.BaseObject):
    '''Definitions for a simplistic QTableWIdgetItem-like object'''

    def __init__(self, index):
        super(QTableModelItem, self).__init__()

        self.index = index

    def text(self):
        return self.index.model().data(self.index, QtCore.Qt.EditRole)

    def setText(self, text):
        self.index.model().setData(self.index, text, QtCore.Qt.EditRole)
