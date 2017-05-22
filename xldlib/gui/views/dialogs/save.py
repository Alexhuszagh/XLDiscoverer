'''
    Views/Dialogs/save
    __________________

    Locks GUI with responsive element during I/O events.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules/submodules
import time

from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from .base import Dialog

# TITLES
# ------

TITLES = {
    'save': 'Saving',
    'load': 'Loading',
    'sort': 'Sorting'
}


# DIALOG
# ------


@logger.init('gui', 'DEBUG')
class IoDialog(Dialog):
    '''Locks GUI from user during long task, such as I/O events'''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'io'

    def __init__(self, mode='save', parent=None):
        super(IoDialog, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_layout(QtGui.QHBoxLayout, alignment='HCenter')
        self.set_window_data(mode)
        self.set_spinner()

        self.set_fixed_size_qt()

    #  EVENT HANDLING

    def showEvent(self, event):
        self.move_qt()
        self.spinner.start()
        event.accept()
        time.sleep(0.1)

    def hideEvent(self, event):
        time.sleep(0.1)
        self.spinner.stop()
        event.accept()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    #     SETTERS

    def set_window_data(self, mode):
        '''Store default window configurations for dialog'''

        self.setWindowTitle(self.get_title(mode))
        self.set_window_nobuttons()

    def set_spinner(self):
        '''Add waiting spinner to layout'''

        self.spinner = widgets.QtWaitingSpinner(self)
        self.spinner.roundness = 70.0
        self.spinner.min_opacity = 15.0
        self.spinner.tail_fade = 70.0
        self.spinner.lines = 12
        self.spinner.line_length = 10
        self.spinner.line_width = 5
        self.spinner.inner_radius = 10
        self.spinner.periodicity = 1
        self.spinner.color = QtGui.QColor('#dadbde')
        self.layout.addWidget(self.spinner)

    #     GETTERS

    @staticmethod
    def get_title(mode):
        return '{}...'.format(TITLES[mode])
