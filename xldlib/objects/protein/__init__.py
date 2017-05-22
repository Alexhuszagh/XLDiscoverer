'''
    Objects/Protein
    _______________

    Datasets for protein storage, loading, and matching.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .database import (LimitedDatabase, ProteinModel,
                       ProteinTable, PROTEIN_FIELDS)
from .mowse import MowseDatabase

__all__ = [
    'fasta',
    'mowse',
    'peptide',
    'peptidelist',
    'permutations',
    'protease',
    'sequencetools'
]
