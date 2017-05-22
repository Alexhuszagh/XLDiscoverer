'''
    Qt/Objects/views
    ________________

    Base class definitions shared by all views.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import abc

from PySide import QtGui

from xldlib.qt import resources as qt

from .base import BaseObject


__all__ = [
    'ViewObject',
    'BaseView',
    'BaseChildView'
]


# OBJECTS
# -------


class ViewObject(BaseObject):
    '''Base class definition for objects derived from QWidgets'''

    #     PUBLIC

    def set_layout(self, cls, clsargs=(), alignment=None):
        '''
        Instantiate, bind and set layout to widget instance.
        See `__layout` for full arg specs.
        '''

        self.layout = self.__layout(cls, clsargs, alignment)
        self.setLayout(self.layout)

    def add_layout(self, cls, clsargs=(), alignment=None):
        '''
        Instantiate and add layout to widget instance.
        See `__layout` for full arg specs.

        Returns (QLayout): custom Qt layout
        '''

        layout = self.__layout(cls, clsargs, alignment)
        self.layout.addLayout(layout)
        return layout

    def add_spacer(self, layout=None, args=()):
        '''
        Add an empty `QLabel` to the view `layout`

        Args:
            layout (None, QLayout): QLayout to add spacer to
            args (iterable): arguments to pass to `addWidget` method
        '''

        if layout is None:
            layout = self.layout
        layout.addWidget(QtGui.QLabel(''), *args)

    def set_stylesheet(self, key):
        '''
        Set Qt widget style using a pre-defined stylesheet with
        a key-based identifier.

        Args:
            key (str):  stylesheet identifier
        '''

        self.setStyleSheet(qt.STYLESHEETS[key])

    def set_size_policy(self, horizontal=None, vertical=None):
        '''
        Set Qt widget size policy from a policy identifier.

        Args:
            horizontal (QSizePolicy, str):  horizontal SizePolicy
            vertical (QSizePolicy, str):  vertical SizePolicy
        '''

        horizontal = self.__sizepolicychecker(horizontal)
        vertical = self.__sizepolicychecker(vertical)
        self.setSizePolicy(horizontal, vertical)

    def block_once(self, frozenfun):
        '''
        Block Qt signals during a single, frozen function call.

        Args:
            frozenfun (callable):   function to execute without signals
        '''

        signal_state = self.signalsBlocked()
        self.blockSignals(True)
        result = frozenfun()
        self.blockSignals(signal_state)

        return result

    def block(self, state=None):
        '''
        Toggle signal blocking on `widget`, either inverting or setting
        the current block state.

        Args:
            state (bool, None): state to toggle (None to invert current state)
        '''

        if state is None:
            state = self.signalsBlocked()
        self.blockSignals(not state)

    #   NON-PUBLIC

    def __layout(self, cls, clsargs, alignment):
        '''
        Non-public method which instantiates a new Qt layout.

        Args:
            clsargs (tuple): arguments to pass to cls constructor
            alignment (None, str, or AlignmentFlag): alignment for Qt layout
        Returns (QLayout): custom Qt layout
        '''

        layout = cls(*clsargs)
        layout.setAlignment(self.__alignmentchecker(alignment))

        return layout

    #    HELPERS

    @staticmethod
    def __alignmentchecker(alignment):
        '''Normalize QtCore.Qt.AlignmentFlag types'''

        return qt.ALIGNMENT.normalize(alignment)

    @staticmethod
    def __sizepolicychecker(policy):
        '''Normalize QtGui.QSizePolicy.Policy types'''

        return qt.SIZE_POLICY.normalize(policy)


class BaseView(ViewObject):
    '''
    ABC for a Qt view, which implements both  _qt and
    _windowkey properties.
    '''

    #    PROPERTIES

    @abc.abstractproperty
    def _qt(self):
        return

    @abc.abstractproperty
    def _windowkey(self):
        return

    @property
    def qt(self):
        return self._qt

    @property
    def windowkey(self):
        return self._windowkey

    @property
    def qt_window(self):
        return self.qt[self.windowkey]

    @property
    def qt_width(self):
        return self.qt[self.windowkey].w

    @property
    def qt_height(self):
        return self.qt[self.windowkey].h


class BaseChildView(ViewObject):
    '''
    ABC for the child of a primary Qt view, whose Qt parent
    implements both _qt and _windowkey properties.
    '''

    #    PROPERTIES

    @property
    def qt(self):
        return self.parent().qt

    @property
    def windowkey(self):
        return self.parent().windowkey

    @property
    def qt_window(self):
        return self.parent().qt_window

    @property
    def qt_width(self):
        return self.parent().qt_width

    @property
    def qt_height(self):
        return self.parent().qt_height
