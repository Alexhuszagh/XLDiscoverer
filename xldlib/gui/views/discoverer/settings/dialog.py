'''
    Gui/Views/Crosslink_Discoverer/settings/dialog
    ______________________________________________

    Dialog to set user preferences.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

from PySide import QtGui

from xldlib.gui.views.dialogs.base import KeyBindingDialog
from xldlib.gui.views import widgets
from xldlib.onstart import args
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import general, pmf, reporterions, search, spreadsheets, transitions


# OBJECTS
# -------

ListItem = namedlist("ListItem", "name cls")


# QLISTVIEW
# ---------

LIST_ITEMS = [
    ListItem('General', general.GeneralSettings),
    ListItem('Search', search.SearchSettings),
    ListItem('Transitions', transitions.TransitionSettings),
    ListItem('Reporter Ions', reporterions.ReporterIonSettings),
    ListItem('PMF', pmf.PmfSettings),
    ListItem('Spreadsheets', spreadsheets.SpreadsheetSettings),
]


@logger.init('gui', 'DEBUG')
class SettingPanel(widgets.ListView):
    '''Lists all the available settings on a panel'''

    def __init__(self, parent):
        super(SettingPanel, self).__init__(parent)

        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)

        self.setHorizontalScrollBarPolicy(qt.SCROLLBAR['AlwaysOff'])

        for list_item in LIST_ITEMS:
            item = QtGui.QStandardItem(list_item.name)
            self.model.appendRow(item)

        self.show()

    #  EVENT HANDLING

    def selectionChanged(self, new, old):
        '''Wrapper which may be used for selectionItemModel'''

        self.parent().settingsview.switch_view(new)
        super(SettingPanel, self).selectionChanged(new, old)


# SETTINGS WIDGET
# ----------------


@logger.init('gui', 'DEBUG')
class SettingsWidget(widgets.Widget):
    '''Widget which toggles between various displays to edit settings'''

    def __init__(self, parent):
        super(SettingsWidget, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)

        self.widget = widgets.Widget()
        self.layout.addWidget(self.widget)

    #     PUBLIC

    def add_widget(self, widget):
        '''Clears the layout and then adds the child widget to the layout.'''

        self.layout.removeWidget(self.widget)
        self.widget.deleteLater()

        self.widget = widget
        self.layout.addWidget(self.widget)

    def switch_view(self, selection):
        '''Toggles the currently visible view based on the current index'''

        index = selection.indexes()[0].row()
        cls = LIST_ITEMS[index].cls
        self.add_widget(cls(self))


# DIALOG
# ------


@logger.init('gui', 'DEBUG')
class SettingsDialog(KeyBindingDialog):
    '''Dialog to add user settings to the selection'''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'settings'

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_layout(QtGui.QHBoxLayout)
        self.set_widgets()
        self.set_window_data()
        self.set_keybindings()

        self.show()

    #     SETTERS

    def set_widgets(self):
        '''Adds the child widgets to the display'''

        self.listview = SettingPanel(self)
        self.layout.addWidget(self.listview, stretch=1)

        self.settingsview = SettingsWidget(self)
        self.layout.addWidget(self.settingsview, stretch=3)

        # select first item in view
        self.listview.setCurrentIndex(self.listview.model.index(0, 0))

    def set_window_data(self):
        '''Sets the window data for the dialog'''

        self.setWindowTitle("Settings")

        self.set_top_window()
        self.set_fixed_size_qt()
        self.move_qt()

    def set_keybindings(self):
        '''Stores the window keybindings depending on the entered mode'''

        self.bind_close()
        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()
