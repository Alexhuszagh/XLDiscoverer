'''
    XlPy/matched/protein_prospector
    _______________________________

    Modules for parsing file formats used for matched peptide
    reporting from peptide search databases (such as Protein
    Prospector, Mascot, Proteome Discoverer).
    Protein Prospector is a registered trademark of The Regents of
    California and is not affiliated with nor endorse XL Discoverer.

    Their website can be found here:
        http://prospector.ucsf.edu/prospector/mshome.htm

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .core import ParseCsv, ParseXml

__all__ = [
    'core',
    'hierarchical',
    'modifications',
]
