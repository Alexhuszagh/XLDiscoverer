'''
    Gui/Views/Visualizer/Trees/checkstate
    _____________________________________

    Class to toggle the checkstates (recursively) in the QTreeView.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore

from xldlib.qt.objects import base
from xldlib.utils import logger

# DATA
# ----

CHECKED_TYPES = {
    'crosslink',
    'charge',
    'isotope'
}


# TREE
# ----


@logger.init('document', 'DEBUG')
class TreeToggleCheckstate(base.BaseObject):
    '''Methods to execute checkstate toggling from the QTreeView.'''

    def __init__(self, parent):
        super(TreeToggleCheckstate, self).__init__(parent)

    #  PUBLIC FUNCTIONS

    def item(self):
        '''Toggles the selected item's checkstate'''

        indexes = self.parent().selectedIndexes()
        for index in indexes:
            self.set_checkstate(index, inverse=True)

    def children(self):
        '''Toggles the selected item's checkstate and its children'''

        indexes = self.parent().selectedIndexes()
        for index in indexes:
            self.set_checkstate_recursive(index)

    #     SETTERS

    def set_checkstate_recursive(self, index, checkstate=None):
        '''Toggles the checkstate of a given index and it's children'''

        item = self.parent().model.itemFromIndex(index)
        group = self.parent().get_group(item, memory=False)
        if group.type in CHECKED_TYPES:

            # toggle the current item
            checked = self.get_checked(item, checkstate, inverse=True)
            self.set_checkstate(index, checkstate=checked)

            # toggle children
            rows = index.model().rowCount(index)
            for row in range(rows):
                modelindex = index.child(row, 0)
                self.set_checkstate_recursive(modelindex, checkstate=checked)

    def set_checkstate(self, index, inverse=False, checkstate=None):
        '''
        Processes the checkstate upon a clicked() signal to toggle
        the checkstate of the widget.
        '''

        item = self.parent().model.itemFromIndex(index)
        group = self.parent().get_group(item, memory=False)

        if group is not None and group.type in CHECKED_TYPES:
            # only toggle if a checkable item
            checked = self.get_checked(item, checkstate, inverse)
            item.setCheckState(QtCore.Qt.CheckState(2 * int(checked)))
            group.setattr('checked', checked)

    #     GETTERS

    @staticmethod
    def get_checked(item, checkstate, inverse):
        '''
        Processes the current widget based on the user definition
        or based on the current checkstate if defined as such.
        '''

        if checkstate is not None:
            return checkstate
        elif inverse:
            return not bool(item.checkState())
        else:
            return bool(item.checkState())


# VISUALIZER
# ----------


@logger.init('document', 'DEBUG')
class VisualizerToggleCheckstate(base.BaseObject):
    '''
    Provides convenience functions to toggle QStandardItem checkstates
    within the QTreeView model from the visualizer window, to facilitate
    binding by keyboard shortcuts.
    '''

    def __init__(self, parent):
        super(VisualizerToggleCheckstate, self).__init__(parent)

    #  PUBLIC FUNCTIONS

    @logger.call('document', 'debug')
    def item(self):
        self.tree().toggle.item()

    @logger.call('document', 'debug')
    def children(self):
        self.tree().toggle.children()

    #     HELPERS

    def tree(self):
        return self.parent().widget.tree
