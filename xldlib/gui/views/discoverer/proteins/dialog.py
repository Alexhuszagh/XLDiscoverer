'''
    Gui/Views/Crosslink_Discoverer/Proteins/dialog
    ______________________________________________

    Dialogs for server queries to the UniProt KB server.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import webbrowser

from collections import OrderedDict

from PySide import QtGui

from xldlib.definitions import partial
from xldlib.gui.views import widgets
from xldlib.gui.views.dialogs.base import Dialog
from xldlib.gui.views.widgets import updating
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# CONSTANTS
# ---------

TAXONOMY = 'http://www.uniprot.org/taxonomy/'

MODES = OrderedDict([
    ('UniProt ID', 'id'),
    ('Mnemonic', 'mnemonic'),
    ('Protein/Gene Name', 'name'),
    ('Sequence', 'sequence')
])


# LISTS
# -----


class BulletItem(widgets.ListWidgetItem):
    '''Subclass with set active/set checked methods'''

    def set_checked(self):
        self.setIcon(qt.IMAGES['disc'])

    def set_unchecked(self):
        self.setIcon(qt.IMAGES['circle'])

    def toggle(self, checkstate):
        if checkstate:
            self.set_checked()
        else:
            self.set_unchecked()


class FilteringMode(widgets.ListWidget):
    '''Definitions for a listwidget object'''

    def __init__(self, parent=None):
        super(FilteringMode, self).__init__(parent)

        self.set_styles()
        self.set_data()
        self.currentItemChanged.connect(self.toggle)

    #    PROPERTIES

    @property
    def filter_mode(self):
        return defaults.DEFAULTS['taxonomy_filtermode']

    @filter_mode.setter
    def filter_mode(self, value):
        defaults.DEFAULTS['taxonomy_filtermode'] = value

    #     SETTERS

    def set_styles(self):
        '''Sets the default styles for the QListView'''

        self.setFlow(self.LeftToRight)
        self.setSelectionMode(qt.SELECTION_MODE['No'])
        self.setVerticalScrollBarPolicy(qt.SCROLLBAR['AlwaysOff'])

        self.setMaximumHeight(0.3 * qt.INCREMENT)
        self.setMinimumWidth(4.5 * qt.INCREMENT)
        self.setStyleSheet("QListWidget { border: 0px solid black }")

    def set_data(self):
        '''Adds the data to the QListWidget'''

        for index, name in enumerate(MODES):
            item = BulletItem(name)
            checked = name == self.filter_mode
            item.toggle(checked)
            self.addItem(item)

            if checked:
                current_index = index

        self.setCurrentRow(current_index)

    #     HELPERS

    def toggle(self, current, previous):
        '''Toggle the currently selected item'''

        previous.set_unchecked()
        current.set_checked()

        self.filter_mode = current.text()


# DIALOGS
# -------


@logger.init('gui', 'DEBUG')
class UniProtDialog(Dialog):
    '''Definitions for a UniProt dialog widget, with a query parameter'''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'uniprot'

    def __init__(self, parent=None):
        super(UniProtDialog, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_layout(QtGui.QGridLayout)
        self.set_taxon()
        self.add_spacer(args=(1, 0, 1, 10))
        self.set_filtering()
        self.set_filteringmode()
        self.add_spacer(args=(4, 0, 1, 10))
        self.set_buttons()

    #  EVENT HANDLING

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    #     SETTERS

    def set_window_data(self):
        '''Stores the default window configurations for the dialog'''

        self.setWindowTitle("UniProt KB Downloader")

        self.set_top_window()
        self.set_window_data()
        self.set_fixed_size_qt()

    def set_taxon(self):
        '''Adds a line edit for the taxonomy download'''

        label = widgets.Label("Taxonomy: ")
        self.layout.addWidget(label, 0, 0, 1, 3)

        storage = updating.Storage('taxonomy')
        taxonomy = updating.LineEdit(self, storage,
            tooltip="Taxonomy ID for the UniProt KB database query.",
            validator=QtGui.QIntValidator())
        self.layout.addWidget(taxonomy, 0, 3, 1, 7)

    def set_filtering(self):
        '''Adds a line edit for a search query filter from the taxonomy'''

        label = widgets.Label("Filter Query: ")
        self.layout.addWidget(label, 2, 0, 1, 3)

        storage = updating.Storage('taxonomy_filter')
        searchquery = updating.LineEdit(self, storage,
            tooltip="String filter for download queries.")
        self.layout.addWidget(searchquery, 2, 3, 1, 7)

    def set_filteringmode(self):
        '''Sets the filtering moder via a QListWidget'''

        filtermode = FilteringMode(self)
        self.layout.addWidget(filtermode, 3, 0, 1, 10, qt.ALIGNMENT['Center'])

    def set_buttons(self):
        '''Adds a submit and get taxonomy buttons to the layout'''

        fun = partial(webbrowser.open, TAXONOMY)
        findtaxa = widgets.ClickButton("Find Taxonomy", fun)
        self.layout.addWidget(findtaxa, 5, 0, 1, 5)

        submit = widgets.ClickButton("Submit", self.submit)
        self.layout.addWidget(submit, 5, 5, 1, 5)

    #     HELPERS

    def submit(self):
        self.hide()
        self.parent().add_from_server()
