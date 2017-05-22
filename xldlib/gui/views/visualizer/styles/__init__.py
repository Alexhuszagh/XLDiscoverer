'''
    Gui/Views/Visualizer/Styles
    ___________________________

    Qt style editors and delegates for visualizer widgets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .colorer import Stylizer
from .delegates import StandardItemDelegate

__all__ = [
    'colorer',
    'delegates'
]
