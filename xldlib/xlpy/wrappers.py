'''
    XlPy/wrappers
    _____________

    Generic function decorators for interacting with the main thread
    instance.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from functools import wraps

from xldlib import exception
from xldlib.onstart.main import APP


# ROWS
# ----


def ignore(code, color='red', bool_=True):
    '''Decorator which emits a message after calling the result'''

    def decorator(f):
        @wraps(f)
        def newf(self, *args, **kwds):
            result = list(f(self, *args, **kwds))
            if result:
                source = APP.discovererthread
                source.files.ignored.update(result)

                message = exception.CODES[code]
                source.helper.emitsequence(message, result, color, bool_)

        return newf
    return decorator


# MESSAGES
# --------


def threadmessage(text, color='black', bool_=False):
    '''Decorator which emits a message after calling the result'''

    def decorator(f):
        @wraps(f)
        def newf(*args, **kwds):
            source = APP.discovererthread
            source.message.emit(text, color, bool_)
            result = f(*args, **kwds)
            return result

        return newf
    return decorator


def warnonerror(error, message, color='green', bool_=True):
    '''Adds a warning upon excepting an error during thread execution'''

    def decorator(f):
        @wraps(f)
        def newf(*args, **kwds):
            try:
                return f(*args, **kwds)
            except error:
                source = APP.discovererthread
                source.message.emit(message, color, bool_)

        return newf
    return decorator


# PROGRESS
# --------


def threadprogress(percent, adjust, condition):
    '''Decorator which updates the running thread's progress'''

    def decorator(f):
        @wraps(f)
        def newf(*args, **kwds):
            result = f(*args, **kwds)
            source = APP.discovererthread
            # /= leads to UnboundLocalError
            if condition(source):
                source.part_done.emit(percent / adjust)
            else:
                source.part_done.emit(percent)

            return result

        return newf
    return decorator


# TERMINATION
# -----------


def threadstop(error, msg):
    '''Decorator which excepts a function call error and closes the thread'''

    def decorator(f):
        @wraps(f)
        def newf(self, *args, **kwds):
            try:
                return f(self, *args, **kwds)
            except error:
                source = APP.discovererthread
                source.isrunning = False
                source.error.emit(msg, error)

        return newf
    return decorator


# CONDITIONAL
# -----------


def runif(condition):
    '''Executes the function call only if the condition evals True'''

    def decorator(f):
        @wraps(f)
        def newf(*args, **kwds):
            source = APP.discovererthread
            if condition(source):
                return f(*args, **kwds)

        return newf
    return decorator
