'''
    Gui/Ui/layouts
    ______________

    Subclasses for various QBoxLayouts

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui


# SCROLL LAYOUT
# -------------


def set_scroll(self, layout):
    '''Sets the scroll area for the desired widget'''

    self.scrollarea = QtGui.QScrollArea()
    self.scrollarea.setWidgetResizable(True)

    self.widget_layout = QtGui.QVBoxLayout(self)
    self.widget_layout.addWidget(self.scrollarea)

    self.widget = QtGui.QWidget()
    self.layout = layout(self.widget)
    self.scrollarea.setWidget(self.widget)



# SHOW EVENTS
# -----------


def hide_layout(self, count=0):
    '''Hides a layout and all child widgets/
    :
        count -- hides everything past this index
    '''

    if self is not None:
        # restrict itemAt from count to total widgets
        for i in range(count, self.count()):
            # use iem ar to hide, not remove
            item = self.itemAt(i)
            try:
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                else:
                    hide_layout(self, item.layout())
            except AttributeError:
                pass


def show_layout(self, count=0):
    '''Shows a layout and all child widgets'''

    if self is not None:
        for i in range(count, self.count()):
            # restrict itemAt from count to total widgets
            item = self.itemAt(i)
            try:
                widget = item.widget()
                if widget is not None:
                    widget.show()
                else:
                    show_layout(self, item.layout())
            except AttributeError:
                pass


# LAYOUTS
# -------


class MenuLayout(QtGui.QHBoxLayout):
    '''
    Centered layout which adds child widgets with equal spacing
    between them.
    '''

    def __init__(self, *widgets):
        '''Calls parent layout and adds widgets to the layout.'''
        super(MenuLayout, self).__init__()

        for widget in widgets:
            self.addStretch(1)
            self.addWidget(widget)

        if widgets:
            self.addStretch(1)
