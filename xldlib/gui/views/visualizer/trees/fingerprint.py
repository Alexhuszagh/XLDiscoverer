'''
    Gui/Views/Visualizer/Trees/fingerprint
    ______________________________________

    QTreeView enabling selection and toggling of the current peptide
    mass fingerprint view.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore

from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import base
from ..io_ import fingerprint


# QTREEVIEW
# ---------


@logger.init('document', 'DEBUG')
class FingerprintTree(base.BaseTreeView):
    '''
    Visualizer for each entry, per file, for the peptide mass fingerprinting
    hits
    '''

    # QT
    # --
    _qt = qt_config.FINGERPRINT
    _selection = 'Single'

    def __init__(self, *args):
        super(FingerprintTree, self).__init__(*args)

        self.set_timers()

        self.io = fingerprint.FingerprintIo(
            self.document, self.model, self._qt)
        #self.stylizer = Stylizer(self)
        #self.zoom = ZoomUtils(self)

    #      SETTERS

    def set_timers(self):
        '''Timers to control reannotating and overcoming glitches'''

        # TODO: fix
        self.resize_timer = QtCore.QTimer(self, singleShot=True)
        # self.resize_timer.timeout.connect(self.reannotate)

        # use the home timer to overcome a bug where the widget does
        # not render properly
        self.home_timer = QtCore.QTimer(self, singleShot=True)
        # self.home_timer.timeout.connect(self.set_mpl_home)
