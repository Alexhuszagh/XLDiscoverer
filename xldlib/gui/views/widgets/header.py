'''
    Gui/Views/Widgets/header
    ________________________

    Base classes for QHeaderView definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.qt.objects import views
from xldlib.qt import resources as qt

__all__ = [
    'HeaderView'
]


# TYPES
# -----

RESIZE_MODE_TYPES = QtGui.QHeaderView.ResizeMode,

# ENUMS
# -----

RESIZE_MODE = qt.Enums(RESIZE_MODE_TYPES, [
    ('Interactive', QtGui.QHeaderView.Interactive),
    ('Fixed', QtGui.QHeaderView.Fixed),
    ('Stretch', QtGui.QHeaderView.Stretch),
    ('ResizeToContents', QtGui.QHeaderView.ResizeToContents),
])


# HEADER
# ------


class HeaderView(QtGui.QHeaderView, views.ViewObject):
    '''QHeaderView which inherits from shared view objects'''

    def __init__(self, orientation, parent=None):
        orientation = self.__orientationchecker(orientation)
        super(HeaderView, self).__init__(orientation, parent)

        self.set_stylesheet('table')

    #     PUBLIC

    def set_resize_mode(self, *args):
        '''
        Set the QHeaderView resizing behavior of individual sections

        Args:
            index (int) (optional):   optional section identifier
            resize_mode (str, enum):  identifier for resize behavior
        '''

        if len(args) == 1:
            self.setResizeMode(self.__resizemodechecker(args[0]))
        elif len(args) == 2:
            index, resize_mode = args
            self.setResizeMode(index, self.__resizemodechecker(resize_mode))
        else:
            raise TypeError("set_resize_mode takes no more than 3 args")

    #     HELPERS

    def __orientationchecker(self, orientation):
        '''Normalize QtCore.Qt.AlignmentFlag types'''

        return qt.ORIENTATION.normalize(orientation)

    def __resizemodechecker(self, resize_mode):
        '''Normalize QtGui.QHeaderView.ResizeMode types'''

        return RESIZE_MODE.normalize(resize_mode)
