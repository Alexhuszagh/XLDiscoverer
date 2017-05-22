'''
    Gui/Views/Windows/fingerprint
    ______________________________________

    Creates a top-level window for a peptide mass fingerprint viewer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.onstart import args
from xldlib.qt import memo
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import visualizer
from .. import menus


# QMAINWINDOW
# -----------


@memo.view
@logger.init('document', 'DEBUG')
class FingerprintWindow(visualizer.VisualizerWindow):
    '''
    Makes a QMainWindow with an embedded QGraphicsScene to select
    and edit peptide mass fingerprints selected for reporting.
    Will display the sequenced, selected for sequencing, and missed ions
    from the MS precursor scan.
    '''

    # QT
    # --
    _qt = qt_config.FINGERPRINT
    _windowkey = 'app'
    _menu = menus.FingerprintMenu

    def __init__(self, document=None):
        super(FingerprintWindow, self).__init__()

        self.document = self._documentchecker(document)
        self.widget = visualizer.VisualizerWidget(
            self.document, 'fingerprint', self)
        self.setCentralWidget(self.widget)

        self.set_rect_qt()
        self.track_window()

        self.set_keybindings()
        self.show()

    #   EVENT HANDLING

    def closeEvent(self, event):
        '''Closes the document upon closure'''

        print("HERE")
        event.accept()

    #     SETTERS

    def set_keybindings(self):
        '''Stores the window keybindings depending on the entered mode'''

        self.bind_close()

        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()

    #      HELPERS

    def _documentchecker(self, item):
        '''Returns a valid document item'''

        return item
