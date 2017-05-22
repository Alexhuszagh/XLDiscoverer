'''
    Gui/Views/Widgets/widget
    ________________________

    Subclasses for QWidgets to inherit from a common object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.controllers import bindings
from xldlib.qt.objects import views


# WIDGETS
# -------


class Widget(QtGui.QWidget, views.BaseView):
    '''Inherits from the base Qt class and the common object'''


class KeyBindingWidget(Widget, bindings.Keys):
    '''QWidget with methods for facilitated keybindings'''
