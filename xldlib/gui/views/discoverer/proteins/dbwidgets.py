'''
    Gui/Views/Crosslink_Discoverer/proteins/dbwidgets
    _________________________________________________

    Widget definitions for protein database configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

from PySide import QtCore

from xldlib.gui.views import widgets
from xldlib.objects import protein
from xldlib.qt import resources as qt
from xldlib.utils import decorators, logger
from xldlib.utils.io_ import qtio


# WIDGETS
# -------


@logger.init('gui', 'DEBUG')
class DatabaseItem(widgets.Push):
    '''Subclass that resizes to a fixed size with a bound folder icon'''

    def __init__(self, title, widget, parent=None):
        self.title = title
        self.widget = widget

        super(DatabaseItem, self).__init__(
            icon=qt.IMAGES['folder_icon'],
            connect=self.__connect,
            parent=parent)

        self.setStyleSheet("")

    #    PROPERTIES

    @property
    def height(self):
        return self.widget.frameSize().height()

    #     PUBLIC

    def resize(self):
        '''Resizes the current icon'''

        size = QtCore.QSize(self.height, self.height)
        self.setFixedSize(size)
        self.setIconSize(size)

    #     HELPERS

    def __connect(self):
        '''Sets the default path from QFileDialog'''

        path = self.widget.text()
        text = qtio.getopenfile(self, self.title, path)
        if text:
            self.widget.store_from_value(text)


# QCOMBOBOX
# ---------


@logger.init('gui', 'DEBUG')
class LimitedDatabaseComboBox(widgets.StylizedBox):
    '''Definitions for an updating QComboBox'''

    def __init__(self, parent, proteins, **kwds):
        super(LimitedDatabaseComboBox, self).__init__(parent)

        self.populate()
        self.proteins = proteins
        self.set_text()

        self.currentIndexChanged.connect(self.store_value)

    #     PUBLIC

    def populate(self):
        '''Populates the QCombobox and the underlying model with values'''

        values = sorted(protein.LimitedDatabase, key=op.itemgetter(1))
        for item in values:
            self.addItem(str(item[0]))

    def set_text(self, text='None'):
        '''Sets the initial text for the current widget'''

        if self.proteins.path is not None:
            text = self.proteins.get_limited(as_string=True)
        self.set_current_text(text)

    @decorators.overloaded
    def store_value(self):
        '''Stores the values upon a value change'''

        if self.proteins.path is not None:
            enum = protein.LimitedDatabase[self.currentText()]
            self.proteins.set_limited(enum)
