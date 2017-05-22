'''
    Gui/Views/Widgets/button
    ________________________

    Checkable, draggable, and icon-embedded QPushButtons

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.qt.objects import views


__all__ = [
    'Button',
    'StandardButton',
    'GradientButton',
    'ClickButton',
    'Push',
    'Save'
]


# BASE
# ----


class Button(QtGui.QPushButton, views.BaseView):
    '''Base class definition for QPushButtons'''


class StandardButton(Button):
    '''Stylized, standard QPushButton'''

    def __init__(self, *args, **kwds):
        super(StandardButton, self).__init__(*args, **kwds)

        self.set_stylesheet('button')


class GradientButton(Button):
    '''Stylized gradient with a checkable QPushButton'''

    def __init__(self, *args, **kwds):
        super(GradientButton, self).__init__(*args, **kwds)

        self.set_stylesheet('gradient_button')


# CLICK
# -----


class ClickButton(StandardButton):
    '''Definitions for a clickable PushButton with a slot to the clicking'''

    def __init__(self, name, slot, **kwds):
        super(ClickButton, self).__init__(name, **kwds)

        self.clicked.connect(slot)


# ICON
# ----


class Push(GradientButton):
    '''Menu icon implementation of QPushButton with bound pixmap'''

    def __init__(self, icon=None, connect=None, parent=None):
        super(Push, self).__init__(parent)

        self.setIcon(icon)
        self.resize()
        if connect is None:
            connect = self.show

        self.clicked.connect(connect)

    def resize(self):
        '''Sets fixed button dimensions based on main_frame width.'''

        width = self.parent().qt['app'].w
        adjust = self.parent().qt['menubutton_size']

        size = int(width * adjust)
        self.setFixedSize(size, size)
        self.setIconSize(QtCore.QSize(size, size))


class Save(Push):
    '''Save icon implementation of QPushButton with bound pixmap'''

    def resize(self, adjust=0.35):
        '''Sets fixed button dimensions based on main_frame width.'''

        size = int(self.parent().qt_width * adjust)
        self.setFixedSize(size, size / 2)
        self.setIconSize(QtCore.QSize(size, size / 2))
