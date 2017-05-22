'''
    Qt/Resources/fonts
    __________________

    Qt font sizes and definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
from PySide import QtGui

__all__ = [
    'DEFAULT_SIZE',
    'HEADER_SIZE',
    'BANNER_SIZE',
    'DRAG_SIZE',
    'BOLD_FONT',
]

# FONT SIZE
# ---------

FONT_SCALAR = 9
DEFAULT_SIZE = FONT_SCALAR
HEADER_SIZE = 12 * FONT_SCALAR // 9
BANNER_SIZE = 18 * FONT_SCALAR // 9
DRAG_SIZE = 14 * FONT_SCALAR // 9


# FONTS
# -----

BOLD_FONT = QtGui.QFont()
BOLD_FONT.setBold(True)
