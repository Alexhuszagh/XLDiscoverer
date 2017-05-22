'''
    Export/OpenOffice
    _________________

    Tools for formatting spreadsheeet data for export to the Office
    Open XML standard via OpenPyXl or the XlsxWriter engines.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .core import OpenOfficeWriter, writematched

__all__ = [
    'base',
    'core',
    'openpyxl_',
    'xlsxwriter_'
]
