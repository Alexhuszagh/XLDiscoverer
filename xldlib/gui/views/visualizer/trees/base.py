'''
    Gui/Views/Visualizer/Trees/base
    _______________________________

    Inheritable QTreeView object providing convenience methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from PySide import QtGui

from xldlib.controllers import bindings
from xldlib.qt import resources as qt
from xldlib.utils import logger

from . import checkstate, movement, nodes
from .. import styles


# VIEW
# ----


@logger.init('document', 'DEBUG')
class BaseTreeView(QtGui.QTreeView, bindings.Keys):
    '''
    Implements base methods for initializing and constructing the QTreeView,
    such as setting the delegate, making the model, etc.
    '''

    def __init__(self, visualizer_view, document, parent):
        super(BaseTreeView, self).__init__(parent)

        self.visualizer_view = visualizer_view
        self.document = self._documentchecker(document)
        self._shift = False

        self.set_ui()
        self.set_viewsize()

        self.nodes = nodes.TreeNodeProcessing(self)
        self.toggle = checkstate.TreeToggleCheckstate(self)
        self.move = movement.TreeNodeMovement(self)
        self.move.set_keybindings()

    #  EVENT HANDLING

    def focusInEvent(self, event):
        '''Overrides the main event to ensure the cursor is a wait'''

        event.accept()
        self.app.setOverrideCursor(qt.CURSOR['Arrow'])

    def selectionChanged(self, new, old):
        '''Wrapper which may be used for selectionItemModel'''

        indexes = self.selectedIndexes()
        self.graphics(indexes, new.indexes(), old.indexes())
        super(BaseTreeView, self).selectionChanged(new, old)

    def mousePressEvent(self, event):
        '''Custom implementation to filter the contiguous selection.'''

        if event.modifiers() & qt.MODIFIER['Shift|Control']:
            self.setSelectionMode(qt.SELECTION_MODE['Extended'])
            self._shift = True
        else:
            # clear if indexes longer
            self.setSelectionMode(qt.SELECTION_MODE['Single'])
            if len(self.selectedIndexes()) > 1:
                self.selectionModel().clearSelection()

        super(BaseTreeView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        '''Custom implementation to filter the congtiguous selection.'''

        if event.modifiers() == qt.MODIFIER['Shift'] or self._shift:
            index = self.indexAt(event.pos())
            item = self.model.itemFromIndex(index)
            checked = bool(item.checkState())
            super(BaseTreeView, self).mouseReleaseEvent(event)

            # recursively change the checkstate, life shift+space
            if bool(item.checkState()) != checked:
                self.toggle.set_checkstate_recursive(
                    index, checkstate=not checked)

        else:
            super(BaseTreeView, self).mouseReleaseEvent(event)
            index = self.indexAt(event.pos())
            if index.isValid():
                # change solely the single index
                self.toggle.set_checkstate(index)

        self._shift = False

    #      SETTERS

    def set_ui(self):
        '''Initializes the visible user elements for the QTreeView'''

        self.set_delegate()
        self.set_model()

    def set_delegate(self):
        '''Makes the StandardItemDelegate for the TreeView'''

        self.delegate = styles.StandardItemDelegate()
        self.setItemDelegate(self.delegate)
        self.setSelectionBehavior(qt.SELECTION_BEHAVIOR['Rows'])
        self.setEditTriggers(qt.EDIT_TRIGGER['No'])

    def set_model(self):
        '''Makes all the foldable elements within the TreeView'''

        self.model = QtGui.QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(self.qt['header'])

        self.setModel(self.model)
        self.setUniformRowHeights(True)
        self.setSelectionMode(qt.SELECTION_MODE[self._selection])

        # set the scrollbar to automatically resize
        self.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)

    def set_viewsize(self):
        '''Returns the view size normalized to specific frame parameters'''

        view_size = self.parent().view.size()
        self.view_size = (5 * view_size / view_size.width())

    #      HELPERS

    def reset_model(self):
        '''Resets the current model, typically after a sort operation'''

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.qt['header'])

        self.io.populate(self.document)
