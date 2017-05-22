'''
    XlPy/Scan_Linkers
    _________________

    Classes for linking precursor/product ion scans from different
    levels.

    Common nomenclature:
        MS1 Scan -- Initial mass acquisition for the intact
            cross-linked peptide
        Precursor scan -- Splits the crosslinker
        Product scan -- Produces the sequencing ions from the isolated
            peptides

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .ms1 import Ms1Linker
from .objects import Row
from .precursor import linkprecursor

__all__ = [
    'precursor',
    'ms1',
    'objects'
]
