'''
    Gui/Views/Dialogs/contextbar
    ____________________________

    Dialog to show user keyboard shortcuts attached to windows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
import math

from PySide import QtCore, QtGui

from xldlib.definitions import partial
from xldlib.gui.views import widgets
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config

from .base import Dialog


# DATA
# ----

KEYICONS = {
    'A': 'keyboard-a',
    'B': 'keyboard-b',
    'C': 'keyboard-c',
    'D': 'keyboard-d',
    'E': 'keyboard-e',
    'F': 'keyboard-f',
    'G': 'keyboard-g',
    'H': 'keyboard-h',
    'I': 'keyboard-i',
    'J': 'keyboard-j',
    'K': 'keyboard-k',
    'L': 'keyboard-l',
    'M': 'keyboard-m',
    'N': 'keyboard-n',
    'O': 'keyboard-o',
    'P': 'keyboard-p',
    'Q': 'keyboard-q',
    'R': 'keyboard-r',
    'S': 'keyboard-s',
    'T': 'keyboard-t',
    'U': 'keyboard-u',
    'V': 'keyboard-v',
    'W': 'keyboard-w',
    'X': 'keyboard-x',
    'Y': 'keyboard-y',
    'Z': 'keyboard-z',
    'Left': 'keyboard-left',
    'Right': 'keyboard-right',
    'Up': 'keyboard-up',
    'Down': 'keyboard-down',
    'Del': 'keyboard-delete',
    'Space': 'keyboard-space',
    'Enter': 'keyboard-enter',
}


# LABELS
# ------


class ShortCutWidget(widgets.Widget):
    '''
    Widget with a bound icon, where the layout includes a left-adjusted
    4x4 icon, a right adjusted 4x2 key command on the top right, and a
    4x2 description on bottom right.
    ----------------
    |      |  KEY  |
    | ICON |--------
    |      |  DES  |
    ----------------
    '''

    # QT
    # --
    _size = 2.0 * qt.INCREMENT

    def __init__(self, shortcut):
        super(ShortCutWidget, self).__init__()

        self.set_layout(QtGui.QGridLayout, alignment='Left')

        icon = IconLabel(KEYICONS[shortcut.key])
        self.layout.addWidget(icon, 0, 0, 4, 4)

        label = widgets.Label(shortcut.sequence)
        label.set_stylesheet('keywhite')
        self.layout.addWidget(label, 0, 4, 2, 6)

        label = widgets.Label(shortcut.description)
        label.set_stylesheet('descriptionwhite')
        self.layout.addWidget(label, 2, 4, 2, 6)

        self.setMaximumSize(self.size, self.size)

    #    PROPERTIES

    @property
    def size(self):
        return self._size


class IconLabel(widgets.Label):
    '''Defines an icon label which spans the same width'''

    # QT
    # --
    _size = 0.5 * qt.INCREMENT

    def __init__(self, iconkey):
        super(IconLabel, self).__init__()

        icon = qt.IMAGES[iconkey]
        pixmap = icon.pixmap(self.size, self.size)
        self.setPixmap(pixmap)
        self.setFixedSize(self.size, self.size)

    @property
    def size(self):
        return self._size


# DIALOGS
# -------


class ContextBar(Dialog):
    '''Definitions for shortcuts attached to a window'''

    # TIMEOUT
    # -------
    timeout = 5000

    # QT
    # --
    _qt = qt_config.CONTEXTS

    def __init__(self, parent, shortcuts):
        super(ContextBar, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_window_data()
        self.set_layout(QtGui.QVBoxLayout)
        self.set_banner()
        self.layout.addStretch(1)
        self.set_shortcuts(shortcuts)
        self.layout.addStretch(1)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.hide)

    #     SETTERS

    def set_window_data(self):
        '''Store the initial window data'''

        self.set_stylesheet('dialog')
        self.setWindowOpacity(0.8)

        self.set_title_qt()
        self.set_window_noframe()
        self.set_fixed_size_qt()
        self.move_qt()

    def set_banner(self):
        '''Add a banner to the layout'''

        layout = self.add_layout(QtGui.QHBoxLayout, alignment='Center')
        banner = widgets.Label("Keyboard Shortcuts")
        banner.set_stylesheet('bannerwhite')
        layout.addWidget(banner)

    def set_shortcuts(self, shortcuts, number=6):
        '''Add images for shortcut labels to the widgets'''

        sublayout = self.add_layout(QtGui.QHBoxLayout)
        sublayouts = []
        for index in range(int(math.ceil(len(shortcuts) / number))):
            layout = QtGui.QVBoxLayout()
            layout.setAlignment(qt.ALIGNMENT['Top|Left'])
            sublayout.addLayout(layout)
            sublayouts.append(layout)

        for index, shortcut in enumerate(shortcuts):
            sublayouts[index // number].addWidget(ShortCutWidget(shortcut))

    #  EVENT HANDLING

    def mousePressEvent(self, event):
        '''Hide on mouse click event and blocks parent events'''

        self.parent().block_once(partial(self.mouse_click, event))

    def mouse_click(self, event):
        '''Hide on Left Prerss'''

        event.accept()
        if event.buttons() == qt.MOUSE['Left']:
            self.hide()

    def showEvent(self, event):
        self.timer.start(self.timeout)
        event.accept()
