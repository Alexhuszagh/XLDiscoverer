'''
    Gui/Views/Widgets/updating
    __________________________

    Widgets with a bound model to allow direct model-view interaction
    upon a given slot or signal.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from namedlist import namedlist, NO_DEFAULT

from PySide import QtCore, QtGui

from xldlib.definitions import partial
from xldlib.gui.views import widgets
from xldlib.qt.objects import views
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger

from . import lineedit, spinbox


# ERRORS
# ------

ERROR = 'Invalid value entered, value must match {}'


# OBJECTS
# -------

Storage = namedlist("Storage", [
    ("key", NO_DEFAULT),
    ("data", defaults.DEFAULTS)]
)


class BaseStorage(views.ViewObject):
    '''Inheritable property definitions for connecting change state/saves'''

    @property
    def store(self):
        return self._store

    @property
    def data(self):
        return self.store.data

    @property
    def key(self):
        return self.store.key

    @property
    def attribute(self):
        return self.data[self.key]

    @attribute.setter
    def attribute(self, value):
        self.data[self.key] = value


class AttrStorage(BaseStorage):
    '''Definitions for writing to mutable (namedlist) values'''

    @property
    def attribute(self):
        '''Returns the current value from the underlying model'''

        if self.attr is not None:
            return getattr(self.data[self.key], self.attr)
        return self.data[self.key]

    @attribute.setter
    def attribute(self, value):
        '''Stores the view value to the model'''

        if self.attr is not None:
            setattr(self.data[self.key], self.attr, value)
            self.data.edited.emit(self.key)
        else:
            self.data[self.key] = value



# QLINEEDIT
# ---------


@logger.init('gui', 'DEBUG')
class LineEdit(lineedit.LineEdit, AttrStorage):
    '''Definitions for an updating line edit'''

    value_about_to_change = QtCore.Signal(str)
    value_changed = QtCore.Signal(bool)

    def __init__(self, parent, store, **kwds):
        super(LineEdit, self).__init__(parent)

        self._store = store

        if 'tooltip' in kwds:
            self.setToolTip(kwds['tooltip'])

        if 'width' in kwds:
            self.setFixedWidth(kwds['width'])

        if 'validator' in kwds:
            self.setValidator(kwds['validator'])

        self.attr = kwds.get('attr')
        self.setText(self.attribute)

        self.editingFinished.connect(self.store_value)

    #  EVENT HANDLING

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        '''Sets the data from the drag'''

        data = event.mimeData()
        if data.hasUrls():
            urls = data.urls()
            self.store_from_value(urls[0].toLocalFile())

        elif data.hasText():
            self.store_from_value(data.text())

    def store_from_value(self, value):
        self.setText(value)
        self.store_value()

    @decorators.overloaded
    def store_value(self):
        '''Signal which then stores le.text() to the model'''

        self.value_about_to_change.emit(self.attribute)
        self.attribute = self.text()
        self.value_changed.emit(True)


# QSPINBOX
# --------


class SpinBoxStorage(BaseStorage):
    '''Definitions to store SpinBox data, with getters and setters'''

    #     PUBLIC

    def set_properties(self, kwds):
        '''Sets the SpinBox properties from a dict'''

        self.adjust = kwds.get('adjust', 1)

        if 'tooltip' in kwds:
            self.setToolTip(kwds['tooltip'])

        if 'width' in kwds:
            self.setFixedWidth(kwds['width'])

        if 'maximum' in kwds:
            self.setMaximum(kwds['maximum'])

        if 'minimum' in kwds:
            self.setMinimum(kwds['minimum'])

        if 'prefix' in kwds:
            self.setPrefix(kwds['prefix'])

        if 'suffix' in kwds:
            self.setSuffix(kwds['suffix'])

        if 'singleStep' in kwds:
            self.setSingleStep(kwds['singleStep'])

        self.set_value()
        self.valueChanged.connect(self.store_value)

    @decorators.overloaded
    def set_value(self):
        self.setValue(self.attribute / self.adjust)

    @decorators.overloaded
    def store_value(self):
        self.attribute = self.value() * self.adjust



@logger.init('gui', 'DEBUG')
class SpinBox(spinbox.SpinBox, SpinBoxStorage):
    '''Definitions for an updating line edit'''

    def __init__(self, parent, store, **kwds):
        super(SpinBox, self).__init__(parent)

        self._store = store
        self.set_properties(kwds)



@logger.init('gui', 'DEBUG')
class DoubleSpinBox(spinbox.DoubleSpinBox, SpinBoxStorage):
    '''Definitions for an updating double spin box'''

    def __init__(self, parent, store, **kwds):
        super(DoubleSpinBox, self).__init__(parent)

        self._store = store
        self.set_properties(kwds)


@logger.init('gui', 'DEBUG')
class ScientificSpinBox(spinbox.ScientificSpinBox, SpinBoxStorage):
    '''Definitions for an updating double spin box in scientific notation'''

    def __init__(self, parent, store, **kwds):
        super(ScientificSpinBox, self).__init__(parent)

        self._store = store
        self.set_properties(kwds)


# QCHECKBOX
# ---------


@logger.init('gui', 'DEBUG')
class CheckBox(QtGui.QCheckBox, BaseStorage):
    '''Definitions for an updating QCheckBox'''

    def __init__(self, text, parent, store, **kwds):
        super(CheckBox, self).__init__(text, parent)

        self._store = store
        self.setChecked(self.attribute)
        self.set_stylesheet('checkbox')

        if 'tooltip' in kwds:
            self.setToolTip(kwds['tooltip'])

        self.stateChanged.connect(self.store_value)

    #     PUBLIC

    @decorators.overloaded
    def store_value(self):
        self.attribute = self.isChecked()


# QCOMBOBOX
# ---------



@logger.init('gui', 'DEBUG')
class ComboBox(widgets.StylizedBox, BaseStorage):
    '''Definitions for an updating QComboBox'''

    def __init__(self, parent, values, store, **kwds):
        super(ComboBox, self).__init__(parent)

        self._store = store
        self.populate(values)
        self.set_current_text(self.attribute)
        self.currentIndexChanged.connect(self.store_value)

    #     PUBLIC

    @decorators.overloaded
    def store_value(self):
        self.attribute = self.currentText()


# QPUSHBUTTON
# -----------


@logger.init('gui', 'DEBUG')
class ClickButton(QtGui.QPushButton, BaseStorage):
    '''Definitions for an updating QComboBox'''

    def __init__(self, parent, store, **kwds):
        super(ClickButton, self).__init__(parent)

        self._store = store
        self.display = kwds.get('display', str)
        self.__connect = kwds.get('connect').__get__(self)

        if 'tooltip' in kwds:
            self.setToolTip(kwds['tooltip'])

        if 'connect' in kwds:
            self.clicked.connect(partial(self.__connect, store))

        self.setText(self.attribute)

    #     PUBLIC

    def setText(self, text):
        '''Override to allow the display function to alter the text'''

        self.__text = text
        super(ClickButton, self).setText(self.display(text))

    def store_from_value(self, value):
        self.setText(value)
        self.store_value()

    @decorators.overloaded
    def store_value(self):
        self.attribute = self.__text
