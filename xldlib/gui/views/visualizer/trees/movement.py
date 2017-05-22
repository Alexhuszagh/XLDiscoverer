'''
    Gui/Views/Visualizer/Trees/movement
    ___________________________________

    Class for changing nodes selection in a QTreeViews via key bindings.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base
from xldlib.utils import logger

# load objects/functions
from collections import OrderedDict


# OBJECTS
# -------


@logger.init('document', 'DEBUG')
class LineMovement(base.BaseObject):
    '''Allows movement of the start and end patches via keysequences'''

    def __init__(self, parent):
        super(LineMovement, self).__init__(parent)

    # PUBLIC FUNCTIONS

    @logger.call('document', 'debug')
    def move(self, name, direction, shift=1):
        '''
        Moves a given line by a certain amount in a given direction
        from the matplotlib widget.
            name -- name of the line to move
            direction -- left or right {-1, 1}
            shift -- indexes to shift
        '''

        if hasattr(self.canvas(), "selection"):
            crosslink = self.canvas().group.get_labels()[0]

            index = crosslink.get_relative_peak_index(name)
            new = self.get_newindex(crosslink, name, index, direction, shift)
            crosslink.set_peak_index(name, new)

            line = getattr(self.canvas(), name)()
            self.draw(line, crosslink, new)
            self.parent().updater.store(self.canvas().group)

    #     GETTERS

    def get_newindex(self, crosslink, line, index, direction, shift):
        '''Returns the new index'''

        index += direction * shift
        if direction < 0 and line == 'start':
            return max(0, index)
        elif direction < 0:
            return max(crosslink.get_relative_peak_index('start'), index)
        elif direction > 0 and line == 'end':
            window = crosslink.get_labels().get_window_indexes()
            return min(index, window.end - window.start)
        elif direction > 0:
            return min(index, crosslink.get_relative_peak_index('end'))

    #     HELPERS

    def model(self):
        return self.parent().model

    def widget(self):
        return self.parent().visualizer_view.widget

    def canvas(self):
        try:
            return self.widget().canvas
        except AttributeError:
            pass

    def draw(self, line, crosslink, index):
        '''Places the line at the new position and updates the canvas'''

        start = crosslink.get_labels().window_start
        x = self.widget().xdata[index + start]
        line.setValue(x)


@logger.init('document', 'DEBUG')
class TreeNodeMovement(base.BaseObject):
    '''
    Provides convenience functions to move up or down within the
    QStandardItemModel of the QTreeView, which allows motion within
    the tree bound to key sequences.
    '''

    def __init__(self, parent):
        super(TreeNodeMovement, self).__init__(parent)

    # PUBLIC FUNCTIONS

    @logger.call('document', 'debug')
    def up(self):
        '''Moves the index up from the current selected index.'''

        newindexes = self.__get_newindexes()

        if newindexes:
            self.set_selection(newindexes)
        else:
            if self.model().rowCount():
                item = self.model().item(self.model().rowCount() - 1)
                self.parent().setCurrentIndex(item.index())

    @logger.call('document', 'debug')
    def down(self):
        '''Moves the index down from the current selected index.'''

        newindexes = self.__get_newindexes(method='indexBelow')

        if newindexes:
            self.set_selection(newindexes, idx=-1)
        else:
            if self.model().rowCount():
                item = self.model().item(0)
                self.parent().setCurrentIndex(item.index())

    #    GETTERS

    def __get_newindexes(self, method='indexAbove'):
        '''Returns a list of new indexes relative to the current selection'''

        indexes = self.parent().selectedIndexes()
        newindexes = []
        for index in indexes:
            newindexes.append(getattr(self.parent(), method)(index))
        return newindexes

    #    SETTERS

    def set_keybindings(self):
        '''Bind keyboard shortcuts for traversing the QTreeView'''

        shortcuts = OrderedDict()
        shortcuts['Up'] = self.up
        shortcuts['Down'] = self.down

        # vim style
        shortcuts['k'] = self.up
        shortcuts['j'] = self.down

        self.parent().bind_keys(shortcuts)

    def set_selection(self, newindexes, idx=0):
        '''Sets a new selection from the given indexes'''

        # return if invalid index in model
        for index in newindexes:
            if not index.isValid():
                return

        self.parent().setCurrentIndex(newindexes[idx])

    #    HELPERS

    def model(self):
        return self.parent().model

