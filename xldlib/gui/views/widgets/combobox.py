'''
    Gui/Views/Widgets/combobox
    __________________________

    Base classes for QComboBox definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.general import sequence

from .list import ListView


# OBJECTS
# -------


class ListViewBox(QtGui.QComboBox):
    '''A QComboBox with a modified view as a stylized QListView'''

    def __init__(self, *args, **kwds):
        super(ListViewBox, self).__init__(*args, **kwds)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.setInsertPolicy(QtGui.QComboBox.InsertPolicy.NoInsert)

        self.setView(ListView(self))


class LookupViewBox(ListViewBox):
    '''QComboBox with a QListView and an O(1) item lookup'''

    def __init__(self, *args, **kwds):
        super(LookupViewBox, self).__init__(*args, **kwds)

        self._addblank = True
        self._values = sequence.LookupTable()

    #    PROPERTIES

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

    @property
    def lookup(self):
        return self.values.lookup

    @property
    def addblank(self):
        return self._addblank

    @addblank.setter
    def addblank(self, value):
        self._addblank = value

    #      PUBLIC

    def addItem(self, value):
        '''Adds the value to the widget and the underlying model'''

        self.values.append(value)
        super(LookupViewBox, self).addItem(value)

    def clear(self):
        '''Clear the lookup tables, values, and all the items'''

        self.values.clear()
        super(LookupViewBox, self).clear()

    def populate(self, values):
        '''Populates the QCombobox and the underlying model with values'''

        for item in values:
            self.addItem(str(item))

    def set_current_text(self, item):
        '''Sets current item based off of item value.'''

        if self.addblank and not item and item not in self.lookup:
            self.values.append(item)

        index = self.lookup[item]
        self.setCurrentIndex(index)


class StylizedBox(LookupViewBox):
    '''
    Stylized base class which provides tooltips and other parameters
    for the QComboBox views.
    '''

    def __init__(self, parent=None, **kwds):
        super(StylizedBox, self).__init__(parent)

        if 'tooltip' in kwds:
            self.setToolTip(kwds['tooltip'])
