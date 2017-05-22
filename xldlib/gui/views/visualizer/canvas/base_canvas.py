'''
    Gui/Views/Visualizer/Canvas/base_canvas
    _______________________________________

    Widget holder for PyQtGraph canvas

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.gui.views import widgets
from xldlib.utils import logger


# WIDGET
# ------


@logger.init('canvas', 'DEBUG')
class BasePlotItem(widgets.Widget):
    '''Base PyQtGraph widget with shared methods'''

    def __init__(self, parent=None):
        super(BasePlotItem, self).__init__(parent)
