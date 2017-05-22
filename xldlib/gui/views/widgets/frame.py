'''
    Gui/Views/Widgets/frame
    _______________________

    Stylish, sunken QFrame to act a divider between widgets

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import views


# DIVIDER
# -------


class Divider(QtGui.QFrame, views.BaseView):
    '''Raised, horizontal QFrame'''

    def __init__(self, parent=None):
        super(Divider, self).__init__(parent)

        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        self.setFrameShape(QtGui.QFrame.HLine)


class SunkenDivider(Divider):
    '''Sunken-stylesheet, horizontal,frame style'''

    def __init__(self, *args, **kwds):
        super(SunkenDivider, self).__init__(*args, **kwds)

        self.set_stylesheet('frame')
