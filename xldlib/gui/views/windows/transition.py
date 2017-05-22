'''
    Gui/Views/Windows/transition
    ____________________________

    Creates a top-level window for an extracted ion chromatogram
    (transitions) viewer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.gui.views.dialogs import contextbar
from xldlib.onstart import args
from xldlib.qt import memo
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import visualizer
from .. import menus


# CONTEXTS
# --------


class TransitionContext(contextbar.ContextBar):
    _windowkey = 'transitions'


# QMAINWINDOW
# -----------


@memo.view
@logger.init('document', 'DEBUG')
class TransitionWindow(visualizer.VisualizerWindow):
    '''
    Makes a QMainWindow with an embedded QGraphicsScene to select
    and edit transitions for MS quantitation. Will display the current
    average PPM and the dot product for the sum of the transitions.
    '''

    # QT
    # --
    _qt = qt_config.TRANSITIONS
    _windowkey = 'app'
    _menu = menus.TransitionMenu

    def __init__(self, document=None, controller=None):
        super(TransitionWindow, self).__init__()

        self.controller = controller
        self.widget = visualizer.VisualizerWidget(document, 'transition', self)
        self.setCentralWidget(self.widget)

        self.set_rect_qt()
        self.track_window()
        self.set_menu()
        self.set_context()

        self.set_keybindings()
        self.show()

    #    PROPERTIES

    @property
    def tree(self):
        return self.widget.tree

    #   EVENT HANDLING

    def closeEvent(self, event):
        '''Closes the document upon closure'''

        if self.controller is None:
            if self.tree.document is not None:
                self.tree.document.close()
        else:
            self.controller.unpause(mode='transition')

        event.accept()
        self.app.processEvents()

    #     SETTERS

    def set_context(self):
        '''Adds a context bar to the current window'''

        self.context = TransitionContext(self, qt.TRANSITIONS_BAR)
        self.bind_keys({'Ctrl+?': self.context.show})

    def set_keybindings(self):
        '''Stores the window keybindings depending on the entered mode'''

        self.bind_close()
        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()

        if args.PICKLE:
            self.bind_pickle()

    #     BINDINGS

    def bind_pickle(self):
        '''Pickles the current item to an xicfit for training'''

        shortcuts = {'Ctrl+p': self.widget.tree.pickle}
        self.bind_keys(shortcuts)
