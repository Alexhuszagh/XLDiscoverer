'''
    Gui/Controllers/Objects/tableitems
    __________________________________

    Helper functions for a QTableWidget items and cell widgets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os

from PySide import QtGui

from xldlib.qt import resources as qt

# load objects/functions
from collections import namedtuple


# OBJECTS
# -------

QComboBoxData = namedtuple("QComboBoxData", "header widget values cast")


class TableItemHelper(object):
    '''Definition for QTableWidget item helpers'''

    def __init__(self, table, basename=False, *qcomboboxes, **kwds):
        super(TableItemHelper, self).__init__()

        self.table = table
        self.basename = basename

        self.qcomboboxes = {}
        for qcombobox in qcomboboxes:
            self.add_qcombobox_column(qcombobox)

        for name, attr in kwds.items():
            setattr(self, name, attr)

    #    ADDERS

    def add_qcombobox_column(self, qcombobox):
        '''Adds a qcombobox data column to the current holder'''

        qcombobox = self._qcomboboxchecker(qcombobox)
        key = len(self.qcomboboxes)
        self.qcomboboxes[key] = qcombobox

    #    GETTERS

    def get_qcombobox(self, qcombobox, value):
        '''Returns an updating QComboBox cell widget from passed data'''

        qcombobox = self._qcomboboxchecker(qcombobox)
        # item.setSizePolicy(QtGui.QSizePolicy.Expanding,
        #        QtGui.QSizePolicy.Expanding)
        # TODO: install event filter, etc.

    #    HELPERS

    def _qcomboboxchecker(self, qcombobox):
        '''Checks a qcombobox object and returns a suitable namedtuple'''

        if isinstance(qcombobox, QComboBoxData):
            return qcombobox

        elif isinstance(qcombobox, (list, tuple)) and len(qcombobox) == 4:
            return QComboBoxData(*qcombobox)

    def _itemchecker(self, column, item):
        '''Returns a QTableWidgetItem or cell widget to add to the Table'''

        if isinstance(item, bytes):
            item = item.decode('utf-8')
        elif isinstance(item, (QtGui.QWidget, QtGui.QTableWidgetItem)):
            item.setTextAlignment(qt.ALIGNMENT['Center'])
            return item
        elif item is None:
            item = ""

        if self.basename:
            item = os.path.basename(item)

        if column in self.qcomboboxes:
            qcombobox = self.qcomboboxes[column]
            item = self.get_qcombobox(qcombobox, item)

        else:
            item = QtGui.QTableWidgetItem(item)
            item.setTextAlignment(qt.ALIGNMENT['Center'])

        return item
