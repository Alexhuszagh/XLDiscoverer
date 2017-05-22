'''
    Gui/Views/Windows/visualizer
    ____________________________

    Inheritable class for spectral visualizer windows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.dialogs import information, save
from xldlib.gui.views.visualizer import trees
from xldlib.objects.documents import spectra
from xldlib.qt import resources as qt
from xldlib.utils import logger

from .base import KeyBindingMainWindow


# QWIDGET
# -------


@logger.init('document', 'DEBUG')
class VisualizerView(widgets.Widget):
    '''
    Sets the graphical UI for the spectral transitions, and allows
    the user to select a given transition.
    '''

    def __init__(self, parent):
        super(VisualizerView, self).__init__(parent)

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

    #  EVENT HANDLING

    def focusInEvent(self, event):
        '''Overrides the main event to ensure the cursor is a wait'''

        event.accept()
        self.app.setOverrideCursor(qt.ALIGNMENT['HCenter'])


@logger.init('document', 'DEBUG')
class VisualizerWidget(widgets.Widget):
    '''
    Makes a QWidget embedding the visualizer window, with each
    file in a QTreeView and the image in a QWidget-bound PyQtGraph item.
    '''

    # QT
    # --
    _trees = {
        'transition': trees.TransitionTree,
        'fingerprint': trees.FingerprintTree
    }

    def __init__(self, document, mode, parent):
        super(VisualizerWidget, self).__init__(parent)

        self._mode = mode

        self.set_layout(QtGui.QHBoxLayout)
        self.set_treeview(document)

     #      SETTERS

    def set_treeview(self, document):
        '''Sets a QTreeView and plot view bound to the widget'''

        self.view = VisualizerView(self)

        cls = self._trees[self._mode]
        self.tree = cls(self.view, document, self)

        self.layout.addWidget(self.tree, stretch=1)
        self.layout.addWidget(self.view, stretch=3)


# KEY SEQUENCES
# -------------

SHORTKEYS = {
    'L': "expand",
    "H": "collapse"
}

MODIFIERS = {
    '{}': {
        'select': True
    },
    'Ctrl+Shift+{}': {},
    'Shift+{}': {
        'select': True,
        'recurse': True
    }
}


# QMAINWINDOW
# -----------


@logger.init('document', 'DEBUG')
class VisualizerWindow(KeyBindingMainWindow):
    '''
    Provides methods shared by the transition viewer scenes nestled
    within a top-level widget.
    '''

    def __init__(self):
        super(VisualizerWindow, self).__init__()

        self.io = spectra.SpectraIo(self)
        self.nodes = trees.VisualizerNodeProcessing(self)
        self.nodes.set_keybindings()
        self.toggle = trees.VisualizerToggleCheckstate(self)

        self.savedialog = save.IoDialog(parent=self)
        self.loaddialog = save.IoDialog(mode='load', parent=self)
        self.aboutdialog = information.AboutDialog(self)
        self.licensedialog = information.LicenseDialog(self)

        self.set_window_data()
        self.bind_close()

    #      SETTERS

    def set_menu(self):
        '''Sets a QMenuBar to the window'''

        menubar = widgets.MenuBar()
        self.setMenuBar(menubar)
        self.menu = self._menu(self)
        self.menu.set_menus()

    def set_window_data(self):
        '''Sets the window icon, title, and styles'''

        self.set_icon_qt()
        self.set_title_qt()
        self.set_stylesheet_qt()
