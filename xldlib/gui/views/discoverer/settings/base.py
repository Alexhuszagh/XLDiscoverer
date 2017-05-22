'''
    Gui/Views/Crosslink_Discoverer/settings/base
    ____________________________________________

    Inheritable settings for settings widgets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.controllers import messages
from xldlib.gui.views import widgets
from xldlib.qt import resources as qt
from xldlib.utils import logger


# WIDGETS
# -------


@logger.init('gui', 'DEBUG')
class BaseSection(widgets.Widget):
    '''Individual sections widget'''

    def __init__(self, parent):
        super(BaseSection, self).__init__(parent)

        layout = getattr(self, "_layout", QtGui.QVBoxLayout)
        self.set_layout(layout, alignment='Top')

        header = widgets.Label(self._title, font=qt.BOLD_FONT)
        self.layout.addWidget(header)


@logger.init('gui', 'DEBUG')
class BaseSettings(widgets.Widget, messages.BaseMessage):
    '''Inheritable methods for settings widgets'''

    def __init__(self, parent):
        super(BaseSettings, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout, alignment='Top')
