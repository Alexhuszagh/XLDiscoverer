'''
    Gui/Views/Widgets/menu
    ______________________

    Subclasses for QMenu to inherit from a common object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import views


# MENUS
# -----


class Menu(QtGui.QMenu, views.BaseView):
    '''Stylized, base Menu definition'''

    def __init__(self, *args, **kwds):
        super(Menu, self).__init__(*args, **kwds)

        self.set_stylesheet('menu')


class MenuBar(QtGui.QMenuBar, views.BaseView):
    '''Stylized, base MenuBar definition'''

    def __init__(self, *args, **kwds):
        super(MenuBar, self).__init__(*args, **kwds)

        self.set_stylesheet('menu')
