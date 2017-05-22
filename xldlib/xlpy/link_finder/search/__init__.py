'''
    XlPy/Link_Finder/search
    _______________________

    Search utilities, which create a data holder for a given candidate
    link and check if the link is within the theoretical PPM window.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

#from .base import PMFBase
from .crosslink import CheckLink, LinkFactory

__all__ = [
    'base',
    'crosslink',
    'pmf'
]
