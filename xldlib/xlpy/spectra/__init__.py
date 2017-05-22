'''
    XlPy/Spectra
    ____________

    Modules for parsing file formats from extracted vendor file formats
    or vendor files to then search for peptide identification.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .parse import parsespectra

__all__ = [
    'link',
    'mgf',
    'mz5',
    'mzdata',
    'mzml',
    'mzxml',
    'parse',
    'pava',
    'scan_parser'
]
