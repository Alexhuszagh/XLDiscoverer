'''
    Gui/Views/Visualizer/Trees/transition
    _____________________________________

    QTreeView containing all the extracted ion chromatogram levels
    for selection and viewing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six

from PySide import QtCore

from xldlib.export import transitions
from xldlib.objects import documents
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import base, movement, update, zoom
from .. import graphics
from ..io_ import transition


# QTREEVIEW
# ---------


@logger.init('document', 'DEBUG')
class TransitionTree(base.BaseTreeView):
    '''
    Visualizer for each entry, per file, for each of the extracted ion
    chromatogram label groups, then crosslinks, then charges and then
    ions.
    '''

    # QT
    # --
    _qt = qt_config.TRANSITIONS
    _selection = 'Extended'

    def __init__(self, *args):
        super(TransitionTree, self).__init__(*args)

        self.io = transition.TransitionIo(self)
        self.graphics = graphics.TransitionGraphics(self)
        self.sorter = documents.DocumentSorter('transition', self)
        self.zoom = zoom.ZoomTools(self)
        self.updater = update.UpdateFitParameters(self)
        self.line = movement.LineMovement(self)
        self.export = transitions.Exporter()

        self.io.populate(self.document)

    #     GETTERS

    @logger.except_error(TypeError)
    def get_group(self, item, memory=None):
        '''Returns the wrapped HDF5 group from the item data'''

        if isinstance(item, QtCore.QModelIndex):
            item = self.model.itemFromIndex(item)

        generator = (i for i in item.data() if (i is not None and i != ''))
        levels = documents.TransitionLevels(*generator)
        return self.document.getfromlevels(levels, memory)

    #     HELPERS

    def _documentchecker(self, item):
        '''Returns a valid document item'''

        if isinstance(item, documents.TransitionsDocument):
            return item

        elif isinstance(item, six.string_types):
            return documents.TransitionsDocument(item)

        elif item is None:
            return None

    def pickle(self):
        '''Helper for pickling the current item selection'''

        indexes = self.selectedIndexes()
        if not indexes:
            return

        group = self.get_group(self.model.itemFromIndex(indexes[0]))
        if group.type == 'crosslink':
            from xldlib.xlpy.tools.xic_picking import xicfit
            import pickle

            fit = xicfit.get_fitargs(group)
            start = group.get_relative_peak_index('start')
            end = group.get_relative_peak_index('end')

            data = str((pickle.dumps(fit, protocol=2), (start, end),))
            self.app.clipboard().setText(data)

            print("CLIPPED")

