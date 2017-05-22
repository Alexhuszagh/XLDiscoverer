'''
    Gui/Views/Widgets/spinbox
    _________________________

    Subclasses for QSpinBox, QDoubleSpinBox, to inherit from a common
    object, as well as a recipe for a QDoubleSpinBox with support
    for scientific numbers.

    QScientificSpinBox is republished with authorization from
    John David Reaver.

    QScientificSpinBox:
        :author: JDReaver, 2014, http://jdreaver.com/
        :original: https://gist.github.com/jdreaver/0be2e44981159d0854f5

        :modified: Alex Huszagh, 2015
            - Added Python 2 support, a QRegExpValidator, documentation, and increased keyword arguments

    Rest:
        :copyright: (c) 2015 The Regents of the University of California.
        :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.definitions import re
from xldlib.qt.objects import views


# CONSTANTS
# ---------

SCIENTIFIC = r'^(?P<sig>[-+]?\d*\.?\d+)(?:[eE](?P<sign>[-+])?(?P<exp>\d+))?$'


# WIDGETS
# -------


class SpinBox(QtGui.QSpinBox, views.BaseView):
    '''Inherits from the base Qt class and the common object'''

    def __init__(self, *args, **kwds):
        super(SpinBox, self).__init__(*args, **kwds)

        self.set_stylesheet('spinbox')


class DoubleSpinBox(QtGui.QDoubleSpinBox, views.BaseView):
    '''Inherits from the base Qt class and the common object'''

    def __init__(self, *args, **kwds):
        super(DoubleSpinBox, self).__init__(*args, **kwds)

        self.set_stylesheet('spinbox')


class ScientificSpinBox(DoubleSpinBox):
    '''
    Recipe for a QDoubleSpinBox with support for floating point
    numbers in scientific notation.
    '''

    # VALIDATION
    # ----------
    float_regex = re.compile(SCIENTIFIC)
    precision = 1

    def __init__(self, parent=None, **kwds):
        super(ScientificSpinBox, self).__init__(parent, **kwds)

        self.validator = QtGui.QDoubleValidator()
        self.validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)

        self._string = '{{:0.{num}e}}'.format(num=self.precision)
        self.formatter = self._string.format

    #  PUBLIC FUNCTIONS

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.tostr(self.tofloat(text))

    def valueFromText(self, text):
        return self.tofloat(text)

    def textFromValue(self, value):
        return self.tostr(value)

    def stepBy(self, steps):
        value = self.value() + steps * self.singleStep()
        self.lineEdit().setText(self.formatter(value))

    #    HELPERS

    def tofloat(self, text, default=0.):
        '''Returns a floating-point representation from text'''

        match = self.float_regex.match(text)
        if match is not None:
            return self.frommatch(match)
        return default

    def tostr(self, value):
        return self.formatter(value)

    @staticmethod
    def frommatch(match):
        '''Converts a match group to a floating point representation'''

        sig, sign, exp = match.groups()
        if sign is None:
            sign = '+'
        if exp is None:
            exp = '0'
        return float(sig) * (10 ** int(sign + exp))
