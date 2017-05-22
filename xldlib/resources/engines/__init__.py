'''
    Resources/Engines
    _________________

    Defines settings and other parameters for spectral formats and
    peptide database search engines.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .search import MATCHED_FORMATS, SEARCH
from .spectra import SPECTRA, SPECTRAL_FORMATS

__all__ = [
    'dicttools',
    'search',
    'spectra',
]
