'''
    Objects/Protein/Database
    ________________________

    Database definitions for protein storage and loading use SQLite.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .proteins import ProteinModel, PROTEIN_FIELDS
from .sequence import LimitedDatabase, ProteinTable

__all__ = [
    'base',
    'proteins',
    'sequence',
    'table'
]
