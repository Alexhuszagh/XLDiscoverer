'''
    Gui/Views/Widgets/checkbox
    __________________________

    Base classes for QCheckBox definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.qt.objects import views


# CLICK
# -----


class ClickCheckBox(QtGui.QCheckBox, views.ViewObject):
    '''Definitions for a clickable PushButton with a slot to the clicking'''

    def __init__(self, text, checked, slot):
        super(ClickCheckBox, self).__init__(text)

        self.setChecked(checked)
        self.clicked.connect(slot)
