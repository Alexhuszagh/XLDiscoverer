'''
    XlPy/matched/PepXML
    ___________________

    Definitions for processing pepXML files to the matched PyTables
    format.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .core import PepXmlHandler

__all__ = [
    'core',
    'mascot',
    'protein_prospector',
    'proteome_discoverer'
]
