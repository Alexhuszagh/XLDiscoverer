'''
    Gui/Views/Widgets/lineedit
    _______________________

    Subclasses for QLineEdits to inherit from a common object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import views


# LABELS
# ------


class LineEdit(QtGui.QLineEdit, views.BaseView):
    '''Inherits from the base Qt class and the common object'''

    def __init__(self, *args, **kwds):
        super(LineEdit, self).__init__(*args, **kwds)

        self.set_stylesheet('lineedit')
