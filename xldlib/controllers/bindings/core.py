'''
    Controllers/Bindings/core
    _________________________

    Core ABC with methods to bind QKeySequences to various slots
    defined in other modules within the package.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import sys

from PySide import QtGui

from xldlib.definitions import partial
from xldlib.qt.objects import views

from . import debug, table


# DATA
# ----

TRACERS = {
    'call': debug.trace_functions,
    'line': debug.trace_lines,
    'both': debug.trace_both
}


# QOBJECT
# -------


class Base(views.BaseView):
    '''ABC'''

    #     PUBLIC

    def bind_keys(self, shortcuts):
        '''
        Bind QKeySequences to slots.

        Args:
            shortcuts (dict) -- {QKeySequence: slot} key:value pairs
        '''

        for key, slot in shortcuts.items():
            sequence = self._sequencechecker(key)
            shortcut = QtGui.QShortcut(sequence, self)
            shortcut.activated.connect(slot)

    #    HELPERS

    def _sequencechecker(self, key):
        '''
        Normalize QKeySequence types

        Args:
            key (str, QKeySequence): identifier for a QKeySequence
        Returns (QKeySequence): Key to bind to shortcut
        '''

        if isinstance(key, QtGui.QKeySequence):
            return key
        else:
            return QtGui.QKeySequence(key)


class Keys(Base):
    '''Provides references to custom keybindings'''

    #      BINDINGS

    def bind_save(self, savefun):
        '''Provides the keybindings for saving the current widget'''

        self.bind_keys({'Ctrl+s': savefun})

    def bind_close(self, local=False):
        '''
        Binds keys to close target widget or widget parent.
            local -- close event occurs on current widget or on main_frame
            bind_close()->QShortcut()
        '''

        # find widget targeted by the close event
        widget = self
        if not local:
            while widget.parent():
                widget = widget.parent()

        # set keyboard shortcuts
        shortcuts = {
            'Ctrl+F4': widget.close,
            'Ctrl+Shift+w': self.close}
        self.bind_keys(shortcuts)

    def bind_context(self):
        '''
        Sets a context QDialog that autohides on click.
            bind_context()->QShortcut()
        '''

        shortcuts = {'Ctrl+?': self.status_bar.show}
        self.bind_keys(shortcuts)

    def bind_pdb(self):
        '''Initiates the PDB debugger upon a key sequence'''

        shortcuts = {'Ctrl+d': debug.set_pdb_trace}
        self.bind_keys(shortcuts)

    def bind_trace(self, mode='call'):
        '''Activates the tracer and can be set to 'call' or 'line' mode'''

        tracer = TRACERS[mode]
        shortcuts = {'Ctrl+t': partial(sys.settrace, tracer)}
        self.bind_keys(shortcuts)

    def bind_table(self):
        '''Provides keybindings for QTableWidgets'''

        self._tabletools = table.TableBindings(self)
        self.bind_keys(self._tabletools.shortcuts)
        # TODO: status bar, context, save

