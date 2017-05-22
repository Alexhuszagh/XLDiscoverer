'''
    Gui/Views/Dialogs/export
    ________________________

    Dialogs for licensing and general version information.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.qt import resources as qt

from .base import Dialog


# EXPORT
# ------


class ExportDialog(Dialog):
    '''Creates an export dialog with a bound QListWidget'''

    def __init__(self, document, mode, parent=None):
        super(ExportDialog, self).__init__(parent)

        self.document = document
        self.mode = mode

        self.setWindowTitle("Select Files...")
        self.set_layout(QtGui.QVBoxLayout, aligment='HCenter')
        self.set_listwidget()
        self.set_buttons()

        self.set_top_window()

    #     SETTERS

    def set_listwidget(self):
        '''Add the child files to the QListWidget'''

        self.list = widgets.ListWidget(self)
        self.list.setSelectionMode(qt.SELECTION_MODE['Multi'])
        self.layout.addWidget(self.list)

        if self.document is not None:
            for transition_file in self.document:
                self.list.addItem(transition_file.search)

    def set_buttons(self):
        '''Add the submit/close buttons to the layout'''

        self.layout.addWidget(widgets.Divider(parent=self))
        hlayout = self.add_layout(QtGui.QHBoxLayout)

        submit = widgets.ClickButton("Submit", self.fin)
        hlayout.addWidget(submit)

        close = widgets.ClickButton("Exit", self.close)
        hlayout.addWidget(close)

    #     HELPERS

    def fin(self):
        '''Find and process the document by the currently selected indexes.'''

        if self.mode == "save":
            self.parent().io.saveas(indexes=self.list.selected)
        elif self.mode == 'close':
            self.parent().io.close_files(indexes=self.list.selected)

        self.close()
