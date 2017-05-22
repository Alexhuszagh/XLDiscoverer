'''
    Gui/Views/Visualizer/Graphics/transition
    ________________________________________

    Translates QTreeView selections to PyQtGraph displays.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore

from xldlib.qt.objects import threads
from xldlib.utils import logger

from .. import base, canvas

# CONSTANTS
# ---------
MUTEX = threads.ContextMutex(QtCore.QMutex.Recursive)


# GRAPHICS
# --------


@logger.init('canvas', 'DEBUG')
class TransitionGraphics(base.DocumentChild):
    '''Allows single and multiindexed selections to overlayed plots'''

    def __init__(self, parent):
        super(TransitionGraphics, self).__init__(parent)

        self.plotter = canvas.TransitionPlotter(parent)

    @logger.call('canvas', 'debug')
    def __call__(self, indexes, newindexes, previous_indexes):
        '''Shows the graphic scene for the item.'''

        if indexes == previous_indexes or not indexes:
            return

        with MUTEX:
            if len(indexes) == 1:
                self.plotter(indexes)
            elif len(indexes) > 1 and self._siblingchecker(indexes):
                self.plotter(indexes, newindexes)
            elif len(indexes) > 1:
                self.plotter(None, newindexes)

    #      HELPERS

    def _siblingchecker(self, indexes):
        '''Returns true if all indexes are siblings'''

        index = indexes[0]
        parent = index.parent()

        # grab the reference indexes
        try:
            rows = self.model.itemFromIndex(parent).rowCount()
        except AttributeError:
            rows = len(self.document)

        reference_indexes = {parent.child(i, 0) for i in range(rows)}
        return all(i in reference_indexes for i in indexes)
