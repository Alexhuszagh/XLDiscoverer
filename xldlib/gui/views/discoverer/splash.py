'''
    Gui/Views/Crosslink_Discoverer/splash
    _____________________________________

    Central widget for Crosslink Discoverer, which provides a splash
    menu for various configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.definitions import partial
from xldlib.gui import ui
from xldlib.gui.views import widgets
from xldlib.qt import memo
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import decorators, logger

from . import crosslinkers, input_files, proteins, running, settings


# DATA
# ----

FIRST_ROW_NONQUANTITATIVE = [
    ('input_files', 'input_files_menu', input_files.InputFilesView),
    ('crosslinkers', 'crosslinkers_menu', crosslinkers.CrosslinkerView)
]

FIRST_ROW_QUANTITATIVE = [
    ('input_files', 'input_files_menu', input_files.InputFilesView),
    ('crosslinkers', 'labeling_menu', crosslinkers.CrosslinkerView)
]

FIRST_ROW = [
    FIRST_ROW_NONQUANTITATIVE,
    FIRST_ROW_QUANTITATIVE
]

SECOND_ROW = [
    ('proteins', 'proteins_menu', proteins.ProteinsView),
    ('settings', 'settings_menu', settings.SettingsDialog),
]


# QWIDGET
# -------


@memo.view
@logger.init('gui', 'DEBUG')
class DiscovererMenu(widgets.Widget):
    '''
    Main Discoverer menu. Embedded in the DiscovererWindow
    below a banner. Holds various, toggle-able parameters, enabling
    users to configure XL Discoverer prior prior to running.

    Layout example::
        -----------------
        -  ----   ----  -
        -  -  -   -  -  -
        -  ----   ----  -
        -               -
        -  ----   ----  -
        -  -  -   -  -  -
        -  ----   ----  -
        -----------------
    '''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER

    def __init__(self, parent, quantitative):
        '''
        Args:
            parent (QObject): Qt parent
            quantitative (bool): MS1 quantitative mode
        '''
        super(DiscovererMenu, self).__init__(parent)

        self.quantitative = quantitative

        self.set_layout(QtGui.QVBoxLayout, alignment='HCenter')
        self._setup_menu()

        self.app.discovererwindow.size_changed.connect(self.change_size)

    #      SETUP

    def _setup_menu(self):
        '''Setup menu and add child widgets'''

        self._setup_divider()
        for fun in (self._setup_first_row, self._setup_second_row):
            self.layout.addStretch(1)
            fun()

        self._setup_divider()
        self.layout.addStretch(1)
        self._setup_run()

    def _setup_first_row(self):
        '''Setup quantitative-dependent items (input files, labeling)'''

        for attr, icon, cls in FIRST_ROW[self.quantitative]:
            button = self._setup_menu_item(icon, cls, self.quantitative)
            setattr(self, attr, button)

        self.add_layout(ui.MenuLayout, (self.input_files, self.crosslinkers))

    def _setup_second_row(self):
        '''Setup quantitative-independent items (proteins, settings)'''

        for attr, icon, cls in SECOND_ROW:
            button = self._setup_menu_item(icon, cls)
            setattr(self, attr, button)

        self.add_layout(ui.MenuLayout, (self.proteins, self.settings))

    def _setup_run(self):
        '''Setup click button to execute running thread'''

        layout = self.add_layout(QtGui.QHBoxLayout)
        slot = partial(self.launch, running.RunDiscoverer, self.quantitative)
        run = widgets.ClickButton("Run", slot)
        layout.addWidget(run)

    def _setup_divider(self):
        '''Setup QFrame as a line to divide sections of the layout'''

        self.layout.addStretch(1)
        self.layout.addWidget(widgets.Divider(parent=self))

    def _setup_menu_item(self, iconkey, cls, *args):
        '''Create icon-embedded button to add to layout'''

        icon = qt.IMAGES[iconkey]
        fun = partial(self.launch, cls, *args)

        return widgets.Push(icon=icon, connect=fun, parent=self)

    #     PUBLIC

    @decorators.overloaded
    def change_size(self):
        '''Adjust widget sizes to window size (acts as a Qt slot)'''

        self.input_files.resize()
        self.crosslinkers.resize()
        self.proteins.resize()
        self.settings.resize()

    def launch(self, cls, *args):
        '''Initialize child class instance with self as parent'''

        if cls is not None:
            widget = cls(self, *args)
            if not isinstance(widget, QtGui.QDialog):
                widget.closed.connect(self.close_child)
                self.parent().layout().addWidget(widget)
                self.hide()

            elif isinstance(widget, running.RunDiscoverer):
                widget.exec_()

    def close_child(self, widget):
        '''Remove child widget and deleter underlying Qt objects'''

        self.parent().layout().removeWidget(widget)
        widget.hide()
        widget.deleteLater()

        self.show()


@memo.view
@logger.init('gui', 'DEBUG')
class DiscovererWidget(widgets.Widget):
    '''
    Central widget for the DiscovererWindow, which embeds a banner
    (QLabel, on top) and a a menu (QWidget, on bottom, with
    embedded QPushButtons).

    Layout example::
        -----------------
        -               -
        -----------------
        -               -
        -               -
        -               -
        -----------------
    '''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER
    _windowkey = 'app'

    def __init__(self, parent, quantitative):
        '''
        Args:
            parent (QObject): Qt parent
            quantitative (bool): MS1 quantitative mode
        '''
        super(DiscovererWidget, self).__init__(parent)

        self.quantitative = quantitative
        ui.set_scroll(self, QtGui.QVBoxLayout)

        self._setup_banner()
        self.menu = DiscovererMenu(self, quantitative)
        self.layout.addWidget(self.menu)

        self.show()

    #     SETUP

    def _setup_banner(self):
        '''Setup QHBoxLayout and added banner to layout'''

        layout = self.add_layout(QtGui.QHBoxLayout)

        key = self.app.discovererwindow.qtkey
        self.banner = ui.BannerLabel(self, self.qt[key].banner)
        layout.addWidget(self.banner)

        self.app.discovererwindow.size_changed.connect(self.banner.resize)
