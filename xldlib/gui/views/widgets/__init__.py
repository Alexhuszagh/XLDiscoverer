'''
    Gui/Views/Widgets
    _________________

    Contains small widget classes that are used extensively

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .button import *
from .checkbox import ClickCheckBox
from .combobox import ListViewBox, StylizedBox
from .frame import Divider, SunkenDivider
from .header import HeaderView
from .label import Banner, Label
from .lineedit import LineEdit
from .list import ListView, ListWidget, ListWidgetItem
from .menu import Menu, MenuBar
from .progressbar import ProgressBar
from .spinbox import DoubleSpinBox, ScientificSpinBox, SpinBox
from .table import BaseTableWidget, BaseTableView, TableNoEdit
from .waitspinner import QtWaitingSpinner
from .widget import KeyBindingWidget, Widget

__all__ = [
    'button',
    'checkbox',
    'combobox',
    'frame',
    'header',
    'label',
    'lineedit',
    'list',
    'menu',
    'progressbar',
    'spinbox',
    'table',
    'updating',
    'waitspinner',
    'widget'
]
