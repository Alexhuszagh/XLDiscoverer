'''
    Gui/Views/Visualizer/Trees/nodes
    ________________________________

    Class for expanding and collapsing nodes from QTreeViews.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base
from xldlib.utils import logger

# load objects/functions
from collections import OrderedDict
from xldlib.definitions import partial


# TREE
# ----


@logger.init('document', 'DEBUG')
class TreeNodeProcessing(base.BaseObject):
    '''Methods to execute expansion/collapsing events from the QTreeView.'''

    def __init__(self, parent):
        super(TreeNodeProcessing, self).__init__(parent)

    # PUBLIC FUNCTIONS

    @logger.call('document', 'debug')
    def expand(self, index, recurse, depth=0):
        '''Recursively expands all children from a given model index'''

        if not index.isValid():
            return
        elif recurse:
            self.__recurse(self.expand, index, depth)

        if not self.parent().isExpanded(index):
            # only expand if it can be expanded, otherwise, we want
            # a quick collapse
            item = index.model().itemFromIndex(index)
            if item.hasChildren():
                self.parent().expand(index)

    @logger.call('document', 'debug')
    def collapse(self, index, recurse, depth=0):
        '''Recursively collapses all children from a given model index'''

        if not index.isValid():
            return
        elif recurse:
            self.__recurse(self.collapse, index, depth)

        # now need to do the collapsing
        if self.parent().isExpanded(index):
            self.parent().collapse(index)

        elif not self.parent().isExpanded(index) and depth == 0:
            # want to collapse one more
            parent = index.parent()
            if parent.isValid():
                self.parent().collapse(parent)
                self.parent().setCurrentIndex(parent)

    #    HELPERS

    @staticmethod
    def __recurse(fun, index, depth):
        '''Recursively calls the parent function to expand/collapse children'''

        rows = index.model().rowCount(index)
        for row in range(rows):
            modelindex = index.child(row, 0)
            fun(modelindex, recurse=True, depth=depth + 1)


# VISUALIZER
# ----------


@logger.init('document', 'DEBUG')
class VisualizerNodeProcessing(base.BaseObject):
    '''
    Provides convenience functions to expand/collapse or sort nodes
    within the QStandardItemModel of the QTreeView from the visualizer
    window, to facilitate binding by keyboard shortcuts.
    '''

    def __init__(self, parent):
        super(VisualizerNodeProcessing, self).__init__(parent)

    # PUBLIC FUNCTIONS

    @logger.call('document', 'debug')
    def expand(self, select=False, recurse=False):
        '''Expands all items from the file root or from given selection'''

        if not select:
            self.tree().expandAll()
        else:
            selected_indexes = self.tree().selectedIndexes()
            for index in selected_indexes:
                self.tree().nodes.expand(index, recurse)

    @logger.call('document', 'debug')
    def collapse(self, select=False, recurse=False):
        '''Collapses all items from the file root or from given selection'''

        if not select:
            self.tree().collapseAll()
        else:
            selected_indexes = self.tree().selectedIndexes()
            for index in selected_indexes:
                self.tree().nodes.collapse(index, recurse)

    @logger.call('document', 'debug')
    def sort(self, key):
        '''Sorts the spectral document by the given key'''

        self.tree().sorter(key=key)
        self.tree().reset_model()

    #    SETTERS

    def set_keybindings(self):
        '''Bind keyboard shortcuts for traversing the QTreeView'''

        shortcuts = OrderedDict()
        shortcuts['L'] = partial(self.expand, select=True)
        shortcuts['Shift+L'] = partial(self.expand, select=True, recurse=True)
        shortcuts['Ctrl+Shift+L'] = self.expand

        shortcuts['H'] = partial(self.collapse, select=True)
        shortcuts['Shift+H'] = partial(self.collapse,
            select=True, recurse=True)
        shortcuts['Ctrl+Shift+H'] = self.collapse

        self.parent().bind_keys(shortcuts)

    #     HELPERS

    def tree(self):
        return self.parent().widget.tree

