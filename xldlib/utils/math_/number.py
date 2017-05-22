'''
    Utils/math_/number
    __________________

    Utilities for using numbers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

        >>> isnan(float("nan"))
        True

        >>> isnan(float("inf"))
        False

        >>> isinf(float("inf"))
        True

        >>> isnull(float("inf"))
        True

        >>> isnull(None)
        True

        >>> isnull("")
        False
'''

# load modules
import numpy as np


# CHECKERS
# --------


def isnan(value):
    '''
    Checks to see if a value is nan, which accepts not floats
    (since non-floats, non-ints cannot check for NaN-ness.
    '''

    try:
        return np.isnan(value)
    except TypeError:
        return False


def isinf(value):
    '''
    Checks to see if a value is inf, which accepts not floats
    (since non-floats, non-ints cannot check for NaN-ness.
    '''

    try:
        return np.isinf(value)
    except TypeError:
        return False


def isnull(value):
    '''Returns if the value is a NoneType, NaN, or inf'''

    return value is None or isnan(value) or isinf(value)


def equal(float1, float2, **kwargs):
    '''
    Checks if two floats are equal at a theshold.
    :
        equal(1.0005, 1.0004)->False
    '''

    threshold = kwargs.get("threshold", 1.e-6)
    return abs(float1 - float2) < threshold


# TESTING
# -------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
