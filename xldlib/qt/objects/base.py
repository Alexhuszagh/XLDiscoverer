'''
    Qt/Objects/base
    _______________

    Base class definitions shared by all objects in XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.onstart.main import APP


__all__ = [
    'BaseObject'
]


# OBJECTS
# -------


class BaseObject(QtCore.QObject):
    '''Base class definition for all classes derived from QObjects'''

    # SHARED
    # ------
    app = APP
    desktop = QtGui.QDesktopWidget()

    #    PROPERTIES

    @property
    def desktop_rect(self):
        return self.desktop.availableGeometry()

    @property
    def desktop_width(self):
        return self.desktop_rect.width()

    @property
    def desktop_height(self):
        return self.desktop_rect.height()
