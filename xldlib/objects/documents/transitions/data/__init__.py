'''
    Objects/Documents/Transitions/Data
    __________________________________

    In-memory data table stores for the transitions data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .base import Levels as TransitionLevels
from .document import DOCUMENT_ATTRS, TransitionsDocument

__all__ = [
    'base',
    'crosslink',
    'document',
    'file',
    'isotope',
    'labels'
]
