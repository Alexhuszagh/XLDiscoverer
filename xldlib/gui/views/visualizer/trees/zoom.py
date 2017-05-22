'''
    Gui/Views/Visualizer/Trees/zoom
    _______________________________

    Methods for custom zoom events (such as zoom to percent).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base
from xldlib.utils import logger


# METHODS
# -------


@logger.init('document', 'DEBUG')
class ZoomTools(base.BaseObject):
    '''Toolkit for zoom events on the PyQtGraph'''

    #  PUBLIC FUNCTIONS

    @logger.except_error(AttributeError)
    def zoomin(self, percentage=0.1, axis='x'):
        self.canvas().zoomin(percentage, axis)

    @logger.except_error(AttributeError)
    def zoomout(self, percentage=0.1, axis='x'):
        self.canvas().zoomout(percentage, axis)

    @logger.except_error(AttributeError)
    def home(self):
        return self.canvas().home()

    @logger.except_error(AttributeError)
    def next(self):
        return self.canvas().next()

    @logger.except_error(AttributeError)
    def previous(self):
        return self.canvas().previous()

    #     HELPERS

    def widget(self):
        return self.parent().visualizer_view.widget

    def canvas(self):
        return self.widget().canvas
