'''
    Utils/logger
    ____________

    Custom implementation of logging with handlers for stream loggers.

    Class StreamToLogger is from:
        Author:  Ferry Boender
        Created: August 14, 2011
        License: GNU GPLv3, see licenses/GNU GPLv3.txt for more details.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import logging
import six
import sys
import traceback

from functools import wraps
from logging.handlers import SysLogHandler

from xldlib import exception
from xldlib.onstart import args


__all__ = [
    'call',
    'except_error',
    'init',
    'Logging',
    'raise_error',
    'StreamToLogger',
]


# CONSTANTS
# ---------

FORMAT = (
    '%(asctime)s - '
    '%(name)s - '
    '%(levelname)s - '
    '%(module)s '
    '%(funcName)s - '
    '%(message)s'
)

if six.PY2:
    _LEVELS = logging._levelNames
    LEVELS = [i for i in _LEVELS if isinstance(i, six.string_types)]
elif six.PY3:
    LEVELS = logging._nameToLevel

__all__ += LEVELS
__all__ += map(str.lower, LEVELS)


# DECORATORS
# ----------


def init(name='', level=args.LOG, string="Initialized {}.{}"):
    '''Log class construction.'''

    logger = _getlevel(name, level)

    def decorator(cls):
        '''Override cls initializer to log class construction'''

        init = cls.__init__
        name = cls.__name__
        module = cls.__module__
        oncall = string.format(name, module)

        def newinit(self, *args, **kwds):
            logger(oncall)
            return init(self, *args, **kwds)

        cls.__init__ = newinit
        return cls

    return decorator


def call(name='', level=args.LOG, string="Calling {0} from {1} at line {2}"):
    '''Log on function or method call'''

    logger = _getlevel(name, level)

    def decorator(f):
        '''Store function details and log on call'''

        name = f.__code__.co_name
        line = f.__code__.co_firstlineno
        filename = f.__code__.co_filename
        oncall = string.format(name, line, filename)

        @wraps(f)
        def newf(*args, **kwds):
            logger(oncall)
            return f(*args, **kwds)

        return newf
    return decorator


def raise_error(f):
    '''Decorator for logging errors upon exception handling for methods'''

    dec = exception.except_error(Exception, errorfun=_log_trace, reraise=True)
    return dec(f)


def except_error(error):
    '''Decorator which excepts and logs error but does not re-raise it'''

    dec = exception.except_error(error, errorfun=_log_trace)

    def decorator(f):
        return dec(f)
    return decorator


# STREAM
# ------


class StreamToLogger(object):
    '''
    Pseudo file-like stream object that redirects stdout
    or stderr writes to a logger instance.
    Modified recipe from Ferry Boender, from:
        http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
    '''

    def __init__(self, logger, buffering, level=logging.INFO, retain=False):
        '''
        Args:
            logger (object):        log handler
            buffering (IOBuffer):   text buffer for output
            level (function):       log level threshold
            retain (bool):          boolean if to retain standard buffer
        '''

        # bind instance attributes
        self.logger = logger
        self.level = level
        self.linebuf = ''

        # need to copy over key params
        self.encoding = getattr(buffering, "encoding", "utf-8")
        self.errors = getattr(buffering, "errors", None)

        if retain:
            self.buffering = buffering

    #     PUBLIC

    def write(self, buf):
        '''
        Write to the original buffer, if present, and then writes
        to the current buffer as required.
        '''

        if hasattr(self, "buffering"):
            # write to buffer first, if needed
            self.buffering.write(buf)

        # write to streaming log
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        '''Empty reimplementation for Python3.x support'''


# LOGGER
# ------


class Logging(object):
    '''
    Custom logger implementation that facilitates many shared streaming
    and standard log handlers
    '''

    # LOGGERS
    # -------
    _loggers = []

    def __init__(self, filename, level):
        '''
        Args:
            filename (str):         path to logfile
            level (str, function):  default log threshold
        '''

        # init base
        if '' not in self.loggers:
            logging.basicConfig(filename=filename,
                filemode='w',
                format=FORMAT,
                level=getattr(logging, level))
            self.loggers.append('')

    #    PROPTERTIES

    @property
    def loggers(self):
        return self._loggers

    #     PUBLIC

    def add_logger(self, level, name=''):
        '''
        Add standard, named log handler to loggers

        Args:
            level (str, function):  {'INFO', 'WARN', 'DEBUG', 'CRITICAL'}
            name (str):             logname to fetch
        '''

        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(self._levelchecker(level))
            self.loggers.append(name)

    def add_remote(self, level, name=''):
        '''
        Create SysLogHandler at a remote address
        See `add_logger` for full arg specs
        '''

        # make a new handler
        handler = SysLogHandler(address=('logs3.papertrailapp.com', 25620))
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)

        # add to main logger
        logger = logging.getLogger(name)
        logger.setLevel(self._levelchecker(level))
        logger.addHandler(handler)

    def add_streaming(self, level, bufname, name=None, retain=True):
        '''
        Make streaming logger for buffer.
        See `add_logger` for partial arg specs

        Args:
            name (str):     logname to fetch
            retain (bool):  retain buffer
        '''

        if name is None:
            name = bufname.upper()

        logger = logging.getLogger(name)
        level = self._levelchecker(level)
        logger.setLevel(level)

        buffering = getattr(sys, bufname)
        stream = StreamToLogger(logger, buffering, level, retain=retain)
        setattr(sys, bufname, stream)

    #    NON-PUBLIC

    @staticmethod
    def _levelchecker(level):
        '''Normalize logging levels'''

        if isinstance(level, six.string_types):
            level = getattr(logging, level)
        return level



# PRIVATE
# -------


def _bind_levels():
    '''Bind log levels to the Logging class'''

    # now need to bind levels
    module = sys.modules[__name__]

    keys = [i for i in LEVELS if isinstance(i, six.string_types)]
    levels = list(map(str.lower, keys)) + keys
    for key in levels:
        try:
            level = getattr(logging, key)
            setattr(Logging, key, staticmethod(level))
            setattr(module, key, level)
        except AttributeError:
            pass


def _getlevel(name, level):
    '''Returns a named logger's `name` callable `level`'''

    logger = logging.getLogger(name)
    return getattr(logger, level.lower())


def _log_trace():
    '''Log traceback on exception handling'''

    trace = traceback.format_exc()
    Logging.error(trace)


_bind_levels()
