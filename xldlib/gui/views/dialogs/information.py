'''
    Gui/Views/Dialogs/information
    _____________________________

    Dialogs for licensing and general version information.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib import resources

from .base import Dialog


# DIALOGS
# -------


class InformationDialog(Dialog):
    '''Provides a base class for methods shared between both dialogs'''

    def __init__(self, parent=None):
        super(InformationDialog, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_layout(QtGui.QVBoxLayout, alignment='HCenter')
        self.set_widgets()
        self.set_top_window()

        self.set_fixed_size_qt()
        self.move_qt()

    #     SETTERS

    def set_widgets(self):
        '''Initialize and add widgets to the current layout'''

        self.hlayout = self.add_layout(QtGui.QHBoxLayout)

        self.set_text()
        self.set_metrics()
        self.hlayout.addSpacing(1)
        self.set_close()
        self.hlayout.addSpacing(1)

    def set_text(self):
        '''Create QLabel with text and add to layout'''

        self.label = widgets.Label(self._text)

        self.label.setAlignment(qt.ALIGNMENT['HCenter'])
        self.layout.addWidget(self.label)
        self.layout.addSpacing(1)

    def set_metrics(self):
        '''Set QDialog size dependent on QFontMetrics'''

        metrics = self.label.fontMetrics()
        lines = self._text.splitlines()
        maxline = max(lines, key=len)

        width = metrics.boundingRect(maxline).width() * 1.2
        height = metrics.height() * len(lines) + 40 + 0.2 * qt.INCREMENT

        self.qt_window.w = width
        self.qt_window.h = height
        self.qt.edited.emit(self.windowkey)

    def set_close(self):
        '''Add close button to the layout'''

        # stylesheet from widgets.ClickButton does not work
        close = QtGui.QPushButton("Close")
        width = close.fontMetrics().boundingRect(close.text()).width()
        close.setMaximumWidth(width * 1.5)

        close.clicked.connect(self.hide)
        self.hlayout.addWidget(close)


# ABOUT
# -----

ABOUT_TEXT = 'CrossLink Discoverer\nVersion {0}'.format(resources.VERSION)
if resources.NIGHT_BUILD:
    ABOUT_TEXT += '\nNight build version {0}'.format(resources.NIGHT_BUILD)


class AboutDialog(InformationDialog):
    '''About dialog with user information including version'''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'about'

    # WIDGETS
    # -------
    _text = ABOUT_TEXT

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle("About")


# LICENSE
# -------


class LicenseDialog(InformationDialog):
    '''
    Dialog with embedded license information for the user. Embed
    with QLabels later.
    '''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'license'

    # WIDGETS
    # -------
    _text = resources.ABRIDGED_LICENSE

    def __init__(self, parent=None):
        super(LicenseDialog, self).__init__(parent)

        self.setWindowTitle("License")
