'''
    XlPy/Matched
    ____________

    Modules for parsing file formats used for matched peptide
    reporting from peptide search databases (such as Protein
    Prospector, Mascot, Proteome Discoverer).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .formula import calculateformulas
from .names import addnames
from .parse import ProcessMatchedData

__all__ = [
]
