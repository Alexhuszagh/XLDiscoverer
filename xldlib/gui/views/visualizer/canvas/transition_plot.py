'''
    Gui/Views/Visualizer/Canvas/transition_plot
    ___________________________________________

    Determines plot type from current selection (single, overlayed,
    spectral level) and adds canvas to Widget holder.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import base
from xldlib.qt import resources as qt
from xldlib.utils import logger

from . import transition_canvas

# load objects/functions
from xldlib.definitions import partial


# SELECTION
# ---------

MULTIPLE_SELECTION = {
    'crosslink',
    'charge',
    'isotope'
}


# PLOTTERS
# --------


@logger.init('canvas', 'DEBUG')
class Plotter(base.BaseObject):
    '''Creates the canvas from the index selections'''

    def __init__(self, parent):
        super(Plotter, self).__init__(parent)

    # PUBLIC FUNCTIONS

    @logger.call('canvas', 'debug')
    def single(self, index):
        '''Generates a plot from a single item selection'''

        group = self.parent().get_group(index)
        self.__plot(group)

    @logger.call('canvas', 'debug')
    def multiple(self, indexes):
        '''Generates a plot from a multiple item selection'''

        groups = [self.parent().get_group(i) for i in indexes]
        group = groups[0].parent
        indexes = sorted(group.index(i) for i in groups)
        self.__plot(group, indexes)

    #   PLOTTERS

    def __plot(self, group, indexes=None):
        '''Plots a 2D x/y chromatogram and adds the image to the layout'''

        widget = transition_canvas.QtGraphWidget(self.parent(), group, indexes)
        self.parent().visualizer_view.add_widget(widget)

        # bind signals
        recalculate = partial(self.parent().updater.recalculate, group)
        widget.picked.connect(recalculate)

        store = partial(self.parent().updater.store, group)
        widget.dropped.connect(store)


@logger.init('canvas', 'DEBUG')
class TransitionPlotter(base.BaseObject):
    '''Checks model index selections and calls Plotter'''

    def __init__(self, parent):
        super(TransitionPlotter, self).__init__(parent)

        self.plotter = Plotter(parent)

    @logger.call('canvas', 'debug')
    def __call__(self, indexes, newindexes=None):
        '''Calls the plot utilities on call'''

        if indexes is None:
            self.set_singleselection(newindexes)
        elif len(indexes) == 1:
            if not indexes[0].isValid():
                self.set_blank()
            else:
                self.plotter.single(indexes[0])

        elif len(indexes) > 1:
            if self._selectionchecker(indexes):
                self.plotter.multiple(indexes)
            else:
                self.set_singleselection(newindexes)

    #     SETTERS

    def set_singleselection(self, newindexes):
        '''
        Removes all but the most recent current selection, due to
        hierarchical differences in the selection (all indexes must
        be siblings).
        '''

        self.parent().setSelectionMode(qt.SELECTION_MODE['Single'])
        self.parent().selectionModel().clearSelection()
        self.parent().move.set_selection([newindexes[-1]])

    def set_blank(self):
        '''Createa a blank widget for the plot view'''

        widget = QtGui.QWidget(self.parent())
        self.parent().visualizer_view.add_widget(widget)

    #     HELPERS

    def _selectionchecker(self, indexes):
        '''Checks the current selection to see if it's valid'''

        group = self.parent().get_group(indexes[0])
        if group.type in MULTIPLE_SELECTION:
            return True
        else:
            return False
