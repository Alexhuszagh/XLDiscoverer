'''
    General/number
    ______________

    Mutable numerical recipe. Supports int, float and long (Py2.x only).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import six

from xldlib.utils import serialization

# load objects/functions
from functools import total_ordering


# OBJECTS
# -------


@serialization.register('MutableNumber')
@total_ordering
class MutableNumber(object):
    '''
    Recipe for a mutable number type. All numerical operations operate
    on a bound numerical type {`int`, `long`, `float`}, and returns
    instances of self in operations as a the left-hand operand in an
    operator, while returning instances of `self.number` as a right-hand
    operand.

        >>> n = MutableNumber(1)
        >>> n + 2
        MutableNumber(3)
        >>> 3 + n
        4
    '''

    def __init__(self, number=0):
        super(MutableNumber, self).__init__()

        self.number = number

    #    NUMERICAL

    def __add__(self, other):
        return self._constructor(self.number + other)

    def __iadd__(self, other):
        self.number += other
        return self

    def __radd__(self, other):
        return other + self.number

    def __sub__(self, other):
        return self._constructor(self.number - other)

    def __isub__(self, other):
        self.number -= other
        return self

    def __rsub__(self, other):
        return other - self.number

    def __mul__(self, other):
        return self._constructor(self.number * other)

    def __imul__(self, other):
        self.number *= other
        return self

    def __rmul__(self, other):
        return other * self.number

    def __div__(self, other):
        return self._constructor(op.div(self.number, other))

    def __idiv__(self, other):
        self.number = op.div(self.number, other)
        return self

    def __rdiv__(self, other):
        return op.div(other, self.number)

    def __floordiv__(self, other):
        return self._constructor(op.floordiv(self.number, other))

    def __ifloordiv__(self, other):
        self.number = op.floordiv(self.number, other)
        return self

    def __rfloordiv__(self, other):
        return op.floordiv(other, self.number)

    def __truediv__(self, other):
        return self._constructor(op.truediv(self.number, other))

    def __itruediv__(self, other):
        self.number = op.truediv(self.number, other)
        return self

    def __rtruediv__(self, other):
        return op.truediv(other, self.number)

    def __pow__(self, other):
        return self._constructor(self.number ** other)

    def __ipow__(self, other):
        self.number **= other
        return self

    def __rpow__(self, other):
        return other ** self.number

    def __mod__(self, other):
        return self._constructor(self.number % other)

    def __imod__(self, other):
        self.number %= other
        return self

    def __rmod__(self, other):
        return other % self.number

    def __abs__(self):
        return self._constructor(abs(self.number))

    #       SIGN

    def __neg__(self):
        return self._constructor(-self.number)

    def __pos__(self):
        return self._constructor(+self.number)

    #     BITWISE

    def __lshift__(self, other):
        return self._constructor(self.number << other)

    def __ilshift__(self, other):
        self.number <<= other
        return self

    def __rlshift__(self, other):
        return other << self.number

    def __rshift__(self, other):
        return self._constructor(self.number >> other)

    def __irshift__(self, other):
        self.number >>= other
        return self

    def __rrshift__(self, other):
        return other >> self.number

    def __and__(self, other):
        return self._constructor(self.number & other)

    def __iand__(self, other):
        self.number &= other
        return self

    def __rand__(self, other):
        return other & self.number

    def __or__(self, other):
        return self._constructor(self.number | other)

    def __ior__(self, other):
        self.number |= other
        return self

    def __ror__(self, other):
        return other | self.number

    def __xor__(self, other):
        return self._constructor(self.number ^ other)

    def __ixor__(self, other):
        self.number ^= other
        return self

    def __rxor__(self, other):
        return other ^ self.number

    #    COMPARISON

    def __eq__(self, other):
        return self.number == other

    def __lt__(self, other):
        return self.number < other

    #   CONVERSIONS

    def __int__(self):
        return int(self.number)

    def __complex__(self):
        return complex(self.number)

    def conjugate(self):
        return self.number.conjugate()

    def __float__(self):
        return float(self.number)

    def __round__(self, precision):
        return round(self.number, precision)

    if six.PY2:
        # long only defined in Python 2.x
        def __long__(self):
            return long(self.number)

    #     STRING

    def __repr__(self):
        return 'MutableNumber({})'.format(self.number)

    def __str__(self):
        return str(self.number)

    #     BOOL

    def __bool__(self):
        return bool(self.number)

    def __nonzero__(self):
        return self.__bool__()

    #  SERIALIZATION

    @serialization.tojson
    def __json__(self):
        return type(self.number)(self)

    @classmethod
    def loadjson(cls, data):
        return cls(data)

    #    NON-PUBLIC

    def _constructor(self, number):
        '''Return new numerical constructor, override for subclasses'''

        return type(self)(number)
