'''
    Objects/Documents
    _________________

    Objects for processing and modifying loaded documents.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .sorting import DocumentSorter
from .transitions import (TransitionsDocument, TransitionsDocumentCache,
                          TransitionLevels)

__all__ = [
    'sorting',
    'spectra'
]
