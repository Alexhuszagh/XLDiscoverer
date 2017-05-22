'''
    Gui/Views/VisualizerGraphics/base
    _________________________________

    Translates QTreeView selections to PyQtGraph displays.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import views


# CHILD
# -----


class DocumentChild(views.BaseView):
    '''Base class for a transitions tree child item'''

    #    PROPERTIES

    @property
    def document(self):
        return self.parent().document

    @document.setter
    def document(self, value):
        self.parent().document = value

    @property
    def model(self):
        return self.parent().model

    @property
    def visualizer_view(self):
        return self.parent().visualizer_view

    @property
    def widget(self):
        return self.parent().visualizer_view.widget

    @property
    def qt(self):
        return self.parent()._qt

