'''
    Gui/Views/Widgets/list
    ______________________

    Various subclasses of QListWidget.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import views


# VIEW
# ----


class ListView(QtGui.QListView, views.BaseView):
    '''Base class to inherit from a common object'''

    def __init__(self, *args, **kwds):
        super(ListView, self).__init__(*args, **kwds)

        self.set_stylesheet('listview')


# WIDGET
# ------


class ListWidgetItem(QtGui.QListWidgetItem, views.BaseView):
    '''Base class to inherit from a common object'''


class ListWidget(QtGui.QListWidget, views.BaseView):
    '''Reimplementation to allow selectIndexes'''

    def __init__(self, *args, **kwds):
        super(ListWidget, self).__init__(*args, **kwds)

        self.set_stylesheet('listwidget')

    #   PROPERTIES

    @property
    def selected(self):
        return [i.row() for i in self.selectedIndexes()]


