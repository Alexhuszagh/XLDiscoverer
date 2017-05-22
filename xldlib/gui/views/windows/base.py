'''
    Gui/Views/Windows/base
    ______________________

    Base class for QMainWindows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.controllers import bindings
from xldlib.qt.objects import window


# WINDOWS
# -------


class MainWindow(QtGui.QMainWindow, window.WindowObject):
    '''Base QMainWindow class which inherits from a common objects'''


class KeyBindingMainWindow(MainWindow, bindings.Keys):
    '''QDialog with methods for facilitated keybindings'''
