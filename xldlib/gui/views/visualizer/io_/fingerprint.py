'''
    Gui/Views/Visualizer/IO_/fingerprint
    ____________________________________

    Input/output methods for a peptide mass fingerprint document.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from . import base
from xldlib.utils import logger

# I/O
# ---


@logger.init('document', 'DEBUG')
class FingerprintIo(base.BaseIo):
    '''
    Provides methods for processing I/O events for mass fingerprints
    from a QTreeView widget, with the document being the PyTables spectral
    document, and the model being the QStandardItemModel for the QTreeView.
    '''

    def __init__(self, parent):
        super(FingerprintIo, self).__init__(parent, fileformat='fingerprint')
