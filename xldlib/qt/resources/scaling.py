'''
    Qt/Resources/scaling
    ____________________

    Qt view definitions for window and widget data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.onstart.main import APP


__all__ = [
    'INCREMENT'
]

# CONSTANTS
# ---------

DESKTOP = APP.desktop().geometry()

QUARTER_X = DESKTOP.width() // 4            # ~500, 1920 x H
TOP_Y = DESKTOP.height() // 20              # ~50,  W    x 1080
INCREMENT = DESKTOP.height() // 10          # ~100, W    x 1080
FONT_INTREMENT = INCREMENT
