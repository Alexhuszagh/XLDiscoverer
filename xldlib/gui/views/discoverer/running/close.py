'''
    Gui/Views/Crosslink_Discoverer/close
    ____________________________________

    QDialog warning the user if they want to quit while Crosslink
    Discoverer is running. Can be permanently ignored.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib import exception
from xldlib.gui.views.dialogs.base import Dialog
from xldlib.gui.views import widgets
from xldlib.onstart.main import APP
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# DIALOG
# ------


@logger.init('gui', 'DEBUG')
class RunningClosePopup(Dialog):
    '''
    Dialog box that ensures the user would like to quit while
    calculations are running.
    '''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'running_close'

    def __init__(self, parent=None):
        super(RunningClosePopup, self).__init__(parent, windowTitle="Exit")

        self.set_layout(QtGui.QVBoxLayout, alignment='HCenter')
        self.set_windowdata()

        self.set_widgets()
        self.set_standard_buttons()

    #    PROPERTIES

    @property
    def ignore(self):
        return defaults.DEFAULTS['ignore_running_close']

    @ignore.setter
    def ignore(self, value):
        defaults.DEFAULTS['ignore_running_close'] = value

    #     SETTERS

    def set_windowdata(self):
        '''Sets the window data for the dialog'''

        self.setWindowTitle("Closing...")

        self.resizeEvent = self.ignore_resize_event
        self.moveEvent = self.track_move_event

        self.set_top_window()
        self.set_fixed_size_qt()
        self.move_qt()

    def set_widgets(self, text="Don't ask me again"):
        '''
        Make label above a labelled QCheckbox preventing user
        from accidentally quitting while running calculations.
        '''

        label = widgets.Label(exception.CODES['007'])
        self.layout.addWidget(label)

        self.checkbox = widgets.ClickCheckBox(text, self.ignore, self.update)
        self.layout.addWidget(self.checkbox)

    def set_standard_buttons(self):
        '''Sets the QStandardButtons for QDialog'''

        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        self.box = QtGui.QDialogButtonBox(standardButtons=buttons, parent=self)

        self.layout.addWidget(self.box)
        self.box.clicked.connect(self.close)

    #     HELPERS

    def update(self):
        self.ignore = self.checkbox.isChecked()


# CONTROLLERS
# -----------


@logger.call('gui', 'debug')
def running_closeevent(event):
    '''
    Event Handler for close event which overrides the close until the
    user confirms their choice.
    '''

    if defaults.DEFAULTS['ignore_running_close']:
        event.accept()
        return

    popup = RunningClosePopup(parent=APP.discovererwindow)
    popup.box.accepted.connect(event.accept)
    popup.box.rejected.connect(event.ignore)
    popup.exec_()
