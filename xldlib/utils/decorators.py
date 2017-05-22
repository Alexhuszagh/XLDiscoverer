'''
    Utils/decorators
    ________________

    Function and method decorators to cast, limit, reduce, selectively
    call functions depending on their arguments, argument types, and
    argument number.


        Functions accepts, returns, and info are from:
            https://wiki.python.org/moin/PythonDecoratorLibrary

        Functions cast, overloaded, underloaded are native to XL Discoverer:

        :copyright: (c) 2015 The Regents of the University of California.
        :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.


Docstring for accepts, returns from:
    https://wiki.python.org/moin/PythonDecoratorLibrary

One of three degrees of enforcement may be specified by passing
the 'debug' keyword argument to the decorator:
    0 -- NONE:   No type-checking. Decorators disabled.
 #!python
-- MEDIUM: Print warning message to stderr. (Default)
    2 -- STRONG: Raise TypeError with message.
If 'debug' is not passed to the decorator, the default level is used.

Example usage:
    >>> NONE, MEDIUM, STRONG = 0, 1, 2
    >>>
    >>> @accepts(int, int, int)
    ... @returns(float)
    ... def average(x, y, z):
    ...     return (x + y + z) / 2
    ...
    >>> average(5.5, 10, 15.0)
    TypeWarning:  'average' method accepts (int, int, int), but was given
    (float, int, float)
    15.25
    >>> average(5, 10, 15)
    TypeWarning:  'average' method returns (float), but result is (int)
    15

Needed to cast params as floats in function def (or simply divide by 2.0).

    >>> TYPE_CHECK = STRONG
    >>> @accepts(int, debug=TYPE_CHECK)
    ... @returns(int, debug=TYPE_CHECK)
    ... def fib(n):
    ...     if n in (0, 1): return n
    ...     return fib(n-1) + fib(n-2)
    ...
    >>> fib(5.3)
    Traceback (most recent call last):
      ...
    TypeError: 'fib' method accepts (int), but was given (float)
'''

# load future
from __future__ import print_function

# load modules
import sys

# DECORATORS
# -----------


def accepts(*types, **kw):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.
    kw    -- Optional specification of 'debug' level (this is the only valid
             keyword argument, no other should be given).
             debug = ( 0 | 1 | 2 )

    '''

    if not kw:
        # default level: MEDIUM
        debug = 1
    else:
        debug = kw['debug']
    try:
        def decorator(f):
            def newf(*args):
                if debug is 0:
                    return f(*args)
                assert len(args) == len(types)
                argtypes = tuple(map(type, args))
                for index, arg in enumerate(args):
                    if not isinstance(arg, types[index]):
                #if argtypes != types:
                        msg = info(f.__name__, types, argtypes, 0)
                        if debug is 1:
                            print('TypeWarning: ', msg, file=sys.stderr)
                        elif debug is 2:
                            raise TypeError(msg)
                return f(*args)
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError as key:
        raise KeyError(key + "is not a valid keyword argument")
    except TypeError as msg:
        raise TypeError(msg)


def returns(ret_type, **kw):
    '''Function decorator. Checks decorated function's return value
    is of the expected type.

    Parameters:
    ret_type -- The expected type of the decorated function's return value.
                Must specify type for each parameter.
    kw       -- Optional specification of 'debug' level (this is the only valid
                keyword argument, no other should be given).
                debug=(0 | 1 | 2)
    '''
    try:
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        def decorator(f):
            def newf(*args):
                result = f(*args)
                if debug is 0:
                    return result
                res_type = type(result)
                #if res_type != ret_type:
                if not isinstance(result, ret_type):
                    msg = info(f.__name__, (ret_type,), (res_type,), 1)
                    if debug is 1:
                        print('TypeWarning: ', msg, file=sys.stderr)
                    elif debug is 2:
                        raise TypeError(msg)
                return result
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError as key:
        raise KeyError(key + "is not a valid keyword argument")
    except TypeError as msg:
        raise TypeError(msg)


def cast(*types):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types. If not, converts them to the desired values.
    No error checking, meant to be used with accepts for type warning.
    Specify types.TypeType for no checking.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.
    '''
    def decorator(f):
        def newf(*args):
            args = list(args)
            assert len(args) == len(types)
            argtypes = tuple(map(type, args))
            msg = info(f.__name__, types, argtypes, 2)
            for i, arg in enumerate(args):
                type_ = types[i]
                if not isinstance(arg, type_):
                    try:
                        args[i] = type_(arg)
                    except TypeError:
                        raise TypeError(msg)
            return f(*args)
        newf.__name__ = f.__name__
        return newf
    return decorator


def info(fname, expected, actual, flag):
    '''Convenience function returns nicely formatted error/warning msg.'''

    _format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
    expected, actual = _format(expected), _format(actual)
    msg = "'{0}' method ".format(fname)\
          + ("accepts", "returns", "converts to")[flag] \
          + " ({0}), but ".format(expected)\
          + ("was given", "result is", "was given")[flag] \
          + " ({0})".format(actual)
    return msg


def overloaded(f):
    '''
    Method to provide manual overloading of a given function, which
    is great for typically overloaded static functions bound as Qt slots.
    >>> @overloaded
    >>> def a(x):
    ...    print(x)
    >>> a(1, 2)
    1

    '''
    def decorator(*args, **kwd):
        return f(*args[:f.__code__.co_argcount], **kwd)
    decorator.__name__ = f.__name__
    return decorator


def underloaded(f):
    '''
    Method to provide manual return from a of a given function when provided
    insufficient arguments, ideal for functions bound to static Qt slots.
    >>> @overloaded
    >>> def a(x):
    ...    print(x)
    >>> a(1, 2)
    1

    '''
    def decorator(*args, **kwd):
        if len(args) < f.__code__.co_argcount:
            return
        return f(*args[:f.__code__.co_argcount], **kwd)
    decorator.__name__ = f.__name__
    return decorator
