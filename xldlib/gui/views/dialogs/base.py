'''
    Gui/Views/Windows/base
    ______________________

    Base class for QDialods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.controllers import bindings
from xldlib.qt.objects import window


# DIALOGS
# -------


class Dialog(QtGui.QDialog, window.WindowObject):
    '''Base QDialog class which inherits from a common objects'''


class KeyBindingDialog(Dialog, bindings.Keys):
    '''QDialog with methods for facilitated keybindings'''
