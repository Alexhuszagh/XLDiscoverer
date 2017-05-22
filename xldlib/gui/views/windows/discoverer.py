'''
    Gui/Views/Windows/discoverer
    ____________________________

    Creates a top-level window for either quantitative or non-
    quantitative crosslink discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.onstart import args
from xldlib.qt import memo
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from ..discoverer import splash

# load objects/functions
from .base import KeyBindingMainWindow


# QMAINWINDOW
# -----------


@memo.view
@logger.init('gui', 'DEBUG')
class DiscovererWindow(KeyBindingMainWindow):
    '''
    Generates a top-level widget to launch XL Discoverer for identifying
    and then validating/processing cross-links.
    '''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER
    _windowkey = 'app'
    _qtkey = [
        'default',
        'quantitative'
    ]

    # THREADING
    # ---------
    isrunning = False

    def __init__(self, quantitative):
        super(DiscovererWindow, self).__init__()

        self.quantitative = quantitative

        self.widget = splash.DiscovererWidget(self, quantitative)
        self.setCentralWidget(self.widget)

        self.set_window_data()
        self.set_rect_qt()
        self.track_window()
        self.set_keybindings()

        self.show()

    #    PROPERTIES

    @property
    def qtkey(self):
        return self._qtkey[self.quantitative]

    #     SETTERS

    def set_window_data(self):
        '''Stores the initial window data'''

        windowdata = self.qt[self.qtkey]
        self.setWindowIcon(qt.IMAGES[windowdata.icon])
        self.setWindowTitle(windowdata.title)

        self.set_stylesheet_qt()

    def set_keybindings(self):
        '''Sets the default keybindings for the layout'''

        self.bind_close()
        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()

