'''
    Qt/Resources/flags
    __________________

    Flags to simplify combinations of variables within the Qt library.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

from functools import reduce

import six

from PySide import QtCore

from xldlib.general import mapping


__all__ = [
    'ALIGNMENT',
    'Flags',
    'ITEM',
    'MODIFIER',
    'MOUSE',
    'ORIENTATION',
    'WINDOW_FLAG',
]


# OBJECTS
# -------


class Flags(mapping.HashableDict):
    '''
    Definitions for Qt library flags. Blocks attributes for
    __setitem__ or __delitem__, as well as other mutable methods.
    '''

    # DELIMITER
    # ---------
    delimiter = '|'

    def __init__(self, types, defaults=()):
        super(Flags, self).__init__(defaults)

        self.types = types

    #     PUBLIC

    def normalize(self, flag):
        '''
        Normalize identifier to the proper Qt enum or bitwise or-ed flag.

        Args:
            flag (str, enum):   enum or string to process
        Returns (enum): Returns an enum corresponding to the identifier
        '''

        if isinstance(flag, self.types):
            return flag
        elif isinstance(flag, six.string_types):
            return self[flag]
        return 0

    #      MAGIC

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''Return xored QtCore.Qt flag from key'''

        items = (dict_getitem(self, i) for i in key.split(self.delimiter))
        return reduce(op.or_, items)


# TYPES
# -----

ALIGNMENT_TYPES = (QtCore.Qt.AlignmentFlag, QtCore.Qt.Alignment)
ITEM_TYPES = (QtCore.Qt.ItemFlag, QtCore.Qt.ItemFlags)
MODIFIER_TYPES = (QtCore.Qt.KeyboardModifier, QtCore.Qt.KeyboardModifiers)
MOUSE_TYPES = (QtCore.Qt.MouseButton, QtCore.Qt.MouseButtons)
ORIENTATION_TYPES = (QtCore.Qt.Orientation, QtCore.Qt.Orientations)
WINDOW_FLAG_TYPES = QtCore.Qt.WindowType, QtCore.Qt.WindowFlags,

# DATA
# ----


ALIGNMENT = Flags(ALIGNMENT_TYPES, [
    # horizontal
    ('Left', QtCore.Qt.AlignLeft),
    ('Right', QtCore.Qt.AlignRight),
    ('HCenter', QtCore.Qt.AlignHCenter),
    ('Justify', QtCore.Qt.AlignJustify),

    # vertical
    ('Top', QtCore.Qt.AlignTop ),
    ('Bottom', QtCore.Qt.AlignBottom),
    ('VCenter', QtCore.Qt.AlignVCenter),

    # combinations
    ('Center', QtCore.Qt.AlignCenter),
])

ITEM = Flags(ITEM_TYPES, [
    ('No', QtCore.Qt.NoItemFlags),
    ('Selectable', QtCore.Qt.ItemIsSelectable),
    ('Editable', QtCore.Qt.ItemIsEditable),
    ('DragEnabled', QtCore.Qt.ItemIsDragEnabled),
    ('DropEnabled', QtCore.Qt.ItemIsDropEnabled),
    ('UserCheckable', QtCore.Qt.ItemIsUserCheckable),
    ('Enabled', QtCore.Qt.ItemIsEnabled),
    ('Tristate', QtCore.Qt.ItemIsTristate),
])

MODIFIER = Flags(MODIFIER_TYPES, [
    ('No', QtCore.Qt.NoModifier),
    ('Shift', QtCore.Qt.ShiftModifier),
    ('Control', QtCore.Qt.ControlModifier),
    ('Alt', QtCore.Qt.AltModifier),
    ('Meta', QtCore.Qt.MetaModifier),
    ('Keypad', QtCore.Qt.KeypadModifier),
])

MOUSE = Flags(MOUSE_TYPES, [
    ('No', QtCore.Qt.NoButton),
    ('Left', QtCore.Qt.LeftButton),
    ('Right', QtCore.Qt.RightButton),
    ('Mid', QtCore.Qt.MidButton),
    ('Middle', QtCore.Qt.MiddleButton),
])

ORIENTATION = Flags(ORIENTATION_TYPES, [
    ('Horizontal', QtCore.Qt.Horizontal),
    ('Vertical', QtCore.Qt.Vertical),
])

WINDOW_FLAG = Flags(WINDOW_FLAG_TYPES, [
    ('Widget', QtCore.Qt.Widget),
    ('Window', QtCore.Qt.Window),
    ('Dialog', QtCore.Qt.Dialog),
    ('Sheet', QtCore.Qt.Sheet),
    ('Drawer', QtCore.Qt.Drawer),
    ('Popup', QtCore.Qt.Popup),
    ('Tool', QtCore.Qt.Tool),
    ('ToolTip', QtCore.Qt.ToolTip),
    ('Desktop', QtCore.Qt.Desktop),
    ('Sub', QtCore.Qt.SubWindow),
    ('MSWindowsFixedSizeDialogHint', QtCore.Qt.MSWindowsFixedSizeDialogHint),
    ('MSWindowsOwnDC', QtCore.Qt.MSWindowsOwnDC),
    ('X11BypassWindowManagerHint', QtCore.Qt.X11BypassWindowManagerHint),
    ('FramelessHint', QtCore.Qt.FramelessWindowHint),
    ('CustomizeHint', QtCore.Qt.CustomizeWindowHint),
    ('TitleHint', QtCore.Qt.WindowTitleHint),
    ('SystemMenuHint', QtCore.Qt.WindowSystemMenuHint),
    ('MinimizeButtonHint', QtCore.Qt.WindowMinimizeButtonHint),
    ('MaximizeButtonHint', QtCore.Qt.WindowMaximizeButtonHint),
    ('MinMaxButtonsHint', QtCore.Qt.WindowMinMaxButtonsHint),
    ('CloseButtonHint', QtCore.Qt.WindowCloseButtonHint),
    ('ContextHelpButtonHint', QtCore.Qt.WindowContextHelpButtonHint),
    ('MacToolBarButtonHint', QtCore.Qt.MacWindowToolBarButtonHint),
    ('BypassGraphicsProxyWidget', QtCore.Qt.BypassGraphicsProxyWidget),
    ('ShadeButtonHint', QtCore.Qt.WindowShadeButtonHint),
    ('StaysOnTopHint', QtCore.Qt.WindowStaysOnTopHint),
    ('StaysOnBottomHint', QtCore.Qt.WindowStaysOnBottomHint),
    ('OkButtonHint', QtCore.Qt.WindowOkButtonHint),
    ('CancelButtonHint', QtCore.Qt.WindowCancelButtonHint),
    ('Type_Mask', QtCore.Qt.WindowType_Mask),
])
