'''
    Views/Menus
    ___________

    QMenubar definitions for document views.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .fingerprint import FingerprintMenu
from .transition import TransitionMenu

__all__ = [
    'base',
    'fingerprint',
    'transition'
]
