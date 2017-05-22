'''
    Gui/Views/Windows/splash
    ________________________

    Creates a top-level window for a splash screen, which can then
    be connected to other menus.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.controllers import messages
from xldlib.definitions import partial
from xldlib.gui import ui
from xldlib.gui.views import widgets
from xldlib.gui.views.dialogs import information
from xldlib.onstart import args
from xldlib.qt import memo
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources import MESSAGES
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger

from . import base, discoverer, fingerprint, transition


# DATA
# ----

RESIZABLES = (
    'banner',
    'crosslink_discoverer',
    'fingerprinting',
    'quantitative_discoverer',
    'transition',
)


# QWIDGET
# -------


@memo.view
@logger.init('gui', 'DEBUG')
class SplashMenu(widgets.Widget):
    '''Main menu panel. Holds the various menu options for XL Discoverer'''

    # QT
    # --
    _qt = qt_config.SPLASH
    _windowkey = 'app'
    bannerkey = 'banner'

    def __init__(self, parent):
        super(SplashMenu, self).__init__(parent)

        self.aboutdialog = information.AboutDialog(self)
        self.licensedialog = information.LicenseDialog(self)

        self.set_layout(QtGui.QVBoxLayout, alignment='HCenter')
        self.set_banner()
        self.set_menu()
        self.set_information()

        self.app.splashwindow.size_changed.connect(self.change_size)

    #     SETTERS

    def set_banner(self):
        '''Adds a smooth transform banner to the layout'''

        self.banner = ui.BannerLabel(self, self.bannerkey)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.banner)
        self.layout.addLayout(layout)

    def set_menu(self):
        '''Sets the menu buttons'''

        self.layout.addStretch(1)
        self.layout.addWidget(widgets.Divider(parent=self))

        self.layout.addStretch(1)
        self.set_crosslink_discoverer_layout()

        self.layout.addStretch(1)
        self.set_quantitative_layout()

        self.layout.addStretch(1)
        self.layout.addWidget(widgets.Divider(parent=self))

        self.layout.addStretch(1)

    def set_crosslink_discoverer_layout(self):
        '''Creates a horizontal layout for the Crosslink Discoverer features'''

        self.crosslink_discoverer = self.get_menu_button(
            'xldiscoverer_menu',
            discoverer.DiscovererWindow,
            False)

        self.fingerprinting = self.get_menu_button(
            'fingerprint_menu',
            fingerprint.FingerprintWindow)

        layout = ui.MenuLayout(self.crosslink_discoverer, self.fingerprinting)
        self.layout.addLayout(layout)

    def set_quantitative_layout(self):
        '''Creates a horizontal layout for the Crosslink Discoverer features'''

        self.quantitative_discoverer = self.get_menu_button(
            'quantitative_xldiscoverer_menu',
            discoverer.DiscovererWindow,
            True)

        self.transition = self.get_menu_button(
            'transition_menu',
            transition.TransitionWindow)

        layout = ui.MenuLayout(self.quantitative_discoverer, self.transition)
        self.layout.addLayout(layout)

    def set_information(self):
        '''Adds a license and about dialog to the splash menu'''

        layout = QtGui.QHBoxLayout()

        layout.addStretch(1)
        about = widgets.ClickButton("About", self.aboutdialog.show)
        layout.addWidget(about)

        layout.addStretch(1)
        license = widgets.ClickButton("License", self.licensedialog.show)
        layout.addWidget(license)
        layout.addStretch(1)

        self.layout.addLayout(layout)

    #     GETTERS

    def get_menu_button(self, iconkey, cls, *args):
        '''Creates a menubutton to add to the current display'''

        icon = qt.IMAGES[iconkey]
        fun = partial(self.initchild, cls, *args)

        return widgets.Push(icon=icon, connect=fun, parent=self)

    #     HELPERS

    @decorators.overloaded
    def change_size(self):
        for attr in RESIZABLES:
            getattr(self, attr).resize()

    def initchild(self, cls, *args):
        '''Initializes a child instance class with self as parent'''

        cls(*args)
        self.app.splashwindow.hide()


@memo.view
@logger.init('gui', 'DEBUG')
class SplashView(widgets.Widget, messages.BaseMessage):
    '''Splash screen contain an icon-embedded button menu'''

    def __init__(self, parent):
        super(SplashView, self).__init__(parent)

        ui.set_scroll(self, QtGui.QVBoxLayout)
        self.menu = SplashMenu(self)
        self.layout.addWidget(self.menu)

        self.show()
        self.check_versions()
        self.check_log()

    #    PROPERTIES

    @property
    def send_logs(self):
        return defaults.DEFAULTS['send_logs']

    @send_logs.setter
    def send_logs(self, value):
        defaults.DEFAULTS['send_logs'] = value

    #     HELPERS

    def check_versions(self):
        '''Check XL Discoverer version and available updates.'''

        # TODO: define

    def check_log(self):
        '''Check Xl Discoverer logging defaults.'''

        if self.send_logs is None:
            reply = self.exec_msg(['Yes', 'No'], **MESSAGES['send_logs'])

            if reply == QtGui.QMessageBox.Yes:
                self.send_logs = True

            elif reply == QtGui.QMessageBox.No:
                self.send_logs = False

# QMAINWINDOW
# -----------


@memo.view
@logger.init('gui', 'DEBUG')
class SplashWindow(base.KeyBindingMainWindow):
    '''Window holder for the XL Discoverer splash screen'''

    # QT
    # --
    _qt = qt_config.SPLASH
    _windowkey = 'app'

    def __init__(self):
        super(SplashWindow, self).__init__()

        self.child_widget = SplashView(self)
        self.setCentralWidget(self.child_widget)

        self.set_window_data()
        self.set_rect_qt()
        self.track_window()
        self.set_keybindings()

        self.show()

    #     SETTERS

    def set_window_data(self):
        '''Stores the initial window data'''

        self.set_icon_qt()
        self.set_title_qt()
        self.set_stylesheet_qt()

    def set_keybindings(self):
        '''Sets the default keybindings for the layout'''

        self.bind_close()
        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()
