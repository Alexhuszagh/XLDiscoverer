'''
    Exception/tools
    _______________

    Error handling tool definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import inspect
import warnings

from functools import wraps

__all__ = [
    'except_error',
    'silence_warning'
]


# WARNINGS
# --------


def silence_warning(warning):
    '''
    Decorate function call with a `warnings.simplefilter` to ignore all
    messages from generated from the `warning`.
    '''

    def decorator(f):
        @wraps(f)
        def newf(*args, **kwds):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=warning)
                return f(*args, **kwds)

        return newf
    return decorator


def except_error(error, **kwds):
    '''
    Decorate function call with a try/except block to catch known
    errors to avoid over-indentation and simplify code legibility.

    Args:
        error (Exception):  class which derives from BaseException
    '''

    def decorator(f):
        @wraps(f)
        def newf(*fargs, **fkwds):
            if inspect.isgeneratorfunction(f):
                return _except_generator(error, f, fargs, fkwds, **kwds)
            else:
                return _except_normal(error, f, fargs, fkwds, **kwds)


        return newf
    return decorator


# PRIVATE
# -------


def _except_generator(error, f, fargs, fkwds, **kwds):
    '''
    Silently catches and excepts an error, exhausting the generator
    function until the error is reached.

    See `_except_normal` for full arg specs.
    '''

    try:
        for item in f(*fargs, **fkwds):
            yield item
    except error:
        _handle_error(error, **kwds)


def _except_normal(error, f, fargs, fkwds, **kwds):
    '''
    Non-public method which catches and silently excepts an error
    during function call.

    Args:
        error (Exception):  class which derives from BaseException
        f (callable):       function to call
        fargs (iterable):   sequential arguments to function
        fkwds (mapping):    keyword arguments to function
    '''

    try:
        return f(*fargs, **fkwds)
    except error:
        _handle_error(error, **kwds)


def _handle_error(error, errorfun=None, reraise=False):
    '''
    Intercept error with custom function, such as tracebacks
    or logging.

    Args:
        error (Exception):          handled error
        errorfun (None, function):  function to call on error handling
        reraise (bool):             re-raise the error
    '''

    if errorfun is not None:
        errorfun()
    if reraise:
        raise error
