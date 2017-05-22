'''
    Qt/Resources/enums
    __________________

    Enum identifiers to simplify variable lookups within the
    Qt library.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

from PySide import QtCore, QtGui

from xldlib.general import mapping


__all__ = [
    'CONNECTION',
    'CURSOR',
    'EDIT_TRIGGER',
    'Enums',
    'KEY',
    'MUTEX_RECURSION',
    'SCROLLBAR',
    'SELECTION_BEHAVIOR',
    'SELECTION_MODE',
    'SELECTION_MODEL',
    'SIZE_POLICY',
    'WINDOW',
]

# OBJECTS
# -------


class Enums(mapping.HashableDict):
    '''
    Definitions for Qt library enums. Provides no
    __setitem__ or __delitem__.
    '''

    def __init__(self, types, defaults=()):
        super(Enums, self).__init__(defaults)

        self.types = types

    #     PUBLIC

    def normalize(self, enum):
        '''
        Normalize identifier to the proper Qt enum.

        Args:
            flag (str, enum):   enum or string to process
        Returns (enum): Returns an enum corresponding to the identifier
        '''

        if isinstance(enum, self.types):
            return enum
        elif isinstance(enum, six.string_types):
            return self[enum]
        return 0


# TYPES
# -----

CONNECTION_TYPES = QtCore.Qt.ConnectionType,
CURSOR_TYPES = QtCore.Qt.CursorShape,
EDIT_TRIGGER_TYPES = QtGui.QAbstractItemView.EditTrigger,
KEY_TYPES = QtCore.Qt.Key,
MUTEX_RECURSION_TYPES = QtCore.QMutex.RecursionMode,
SCROLLBAR_TYPES = QtCore.Qt.ScrollBarPolicy,
SELECTION_BEHAVIOR_TYPES = QtGui.QAbstractItemView.SelectionBehavior,
SELECTION_MODE_TYPES = QtGui.QAbstractItemView.SelectionMode,
SELECTION_MODEL_TYPES = QtGui.QItemSelectionModel.SelectionFlag,
SIZE_POLICY_TYPES = QtGui.QSizePolicy.Policy,
WINDOW_TYPES = QtCore.Qt.WindowState,


# DATA
# ----

CONNECTION = Enums(CONNECTION_TYPES, [
    ('Auto', QtCore.Qt.AutoConnection),
    ('Direct', QtCore.Qt.DirectConnection),
    ('Queued', QtCore.Qt.QueuedConnection),
    ('BlockingQueued', QtCore.Qt.BlockingQueuedConnection),
    ('Unique', QtCore.Qt.UniqueConnection),
])

CURSOR = Enums(CURSOR_TYPES, [
    ('Arrow', QtCore.Qt.ArrowCursor),
    ('UpArrow', QtCore.Qt.UpArrowCursor),
    ('Cross', QtCore.Qt.CrossCursor),
    ('Wait', QtCore.Qt.WaitCursor),
    ('IBeam', QtCore.Qt.IBeamCursor),
    ('SizeVer', QtCore.Qt.SizeVerCursor),
    ('SizeHor', QtCore.Qt.SizeHorCursor),
    ('SizeBDiag', QtCore.Qt.SizeBDiagCursor),
    ('SizeFDiag', QtCore.Qt.SizeFDiagCursor),
    ('SizeAll', QtCore.Qt.SizeAllCursor),
    ('Blank', QtCore.Qt.BlankCursor),
    ('SplitV', QtCore.Qt.SplitVCursor),
    ('SplitH', QtCore.Qt.SplitHCursor),
    ('PointingHand', QtCore.Qt.PointingHandCursor),
])

EDIT_TRIGGER = Enums(EDIT_TRIGGER_TYPES, [
    ('No', QtGui.QAbstractItemView.NoEditTriggers),
    ('CurrentChanged', QtGui.QAbstractItemView.CurrentChanged),
    ('DoubleClicked', QtGui.QAbstractItemView.DoubleClicked),
    ('SelectedClicked', QtGui.QAbstractItemView.SelectedClicked),
    ('EditKeyPressed', QtGui.QAbstractItemView.EditKeyPressed),
    ('AnyKeyPressed', QtGui.QAbstractItemView.AnyKeyPressed),
    ('All', QtGui.QAbstractItemView.AllEditTriggers),
])

KEY = Enums(KEY_TYPES, [
    ('Escape', QtCore.Qt.Key_Escape),
    ('Tab', QtCore.Qt.Key_Tab),
    ('Backtab', QtCore.Qt.Key_Backtab),
    ('Backspace', QtCore.Qt.Key_Backspace),
    ('Return', QtCore.Qt.Key_Return),
    ('Enter', QtCore.Qt.Key_Enter),
    ('Insert', QtCore.Qt.Key_Insert),
    ('Delete', QtCore.Qt.Key_Delete),
])

MUTEX_RECURSION = Enums(MUTEX_RECURSION_TYPES, [
    ('Recursive', QtCore.QMutex.Recursive),
    ('NonRecursive', QtCore.QMutex.NonRecursive),
])

SCROLLBAR = Enums(SCROLLBAR_TYPES, [
    ('AsNeeded', QtCore.Qt.ScrollBarAsNeeded),
    ('AlwaysOff', QtCore.Qt.ScrollBarAlwaysOff),
    ('AlwaysOn', QtCore.Qt.ScrollBarAlwaysOn),
])

SELECTION_BEHAVIOR = Enums(SELECTION_BEHAVIOR_TYPES, [
    ('Items', QtGui.QAbstractItemView.SelectItems),
    ('Rows', QtGui.QAbstractItemView.SelectRows),
    ('Columns', QtGui.QAbstractItemView.SelectColumns),
])

SELECTION_MODE = Enums(SELECTION_MODE_TYPES, [
    ('Single', QtGui.QAbstractItemView.SingleSelection),
    ('Contiguous', QtGui.QAbstractItemView.ContiguousSelection),
    ('Extended', QtGui.QAbstractItemView.ExtendedSelection),
    ('Multi', QtGui.QAbstractItemView.MultiSelection),
    ('No', QtGui.QAbstractItemView.NoSelection),
])

SELECTION_MODEL = Enums(SELECTION_MODEL_TYPES, [
    ('NoUpdate', QtGui.QItemSelectionModel.NoUpdate),
    ('Clear', QtGui.QItemSelectionModel.Clear),
    ('Select', QtGui.QItemSelectionModel.Select),
    ('Deselect', QtGui.QItemSelectionModel.Deselect),
    ('Toggle', QtGui.QItemSelectionModel.Toggle),
    ('Current', QtGui.QItemSelectionModel.Current),
    ('Rows', QtGui.QItemSelectionModel.Rows),
    ('Columns', QtGui.QItemSelectionModel.Columns),
    ('SelectCurrent', QtGui.QItemSelectionModel.SelectCurrent),
    ('ToggleCurrent', QtGui.QItemSelectionModel.ToggleCurrent),
    ('ClearAndSelect', QtGui.QItemSelectionModel.ClearAndSelect),
])

SIZE_POLICY = Enums(SIZE_POLICY_TYPES, [
    ('Fixed', QtGui.QSizePolicy.Fixed),
    ('Minimum', QtGui.QSizePolicy.Minimum),
    ('Maximum', QtGui.QSizePolicy.Maximum),
    ('Preferred', QtGui.QSizePolicy.Preferred),
    ('Expanding', QtGui.QSizePolicy.Expanding),
    ('MinimumExpanding', QtGui.QSizePolicy.MinimumExpanding),
    ('Ignored', QtGui.QSizePolicy.Ignored),
])

WINDOW = Enums(WINDOW_TYPES, [
    ('NoState', QtCore.Qt.WindowNoState),
    ('Minimized', QtCore.Qt.WindowMinimized),
    ('Maximized', QtCore.Qt.WindowMaximized),
    ('FullScreen', QtCore.Qt.WindowFullScreen),
    ('Active', QtCore.Qt.WindowActive),
])
