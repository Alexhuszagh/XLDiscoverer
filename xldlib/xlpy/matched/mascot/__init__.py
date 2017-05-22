'''
    XlPy/matched/Mascot
    ___________________

    Utilities to parse Mascot file formats and export formats.
    Mascot is a registered trademark of Matrix Science and
    is not affiliated with nor endorse XL Discoverer. No code from Matrix
    Science (including their Mascot Parser) is used in XL Discoverer.

    Their website can be found here:
        http://www.matrixscience.com/

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .core import ParseMime, ParseXml

__all__ = [
    'core',
    'mime'
]
