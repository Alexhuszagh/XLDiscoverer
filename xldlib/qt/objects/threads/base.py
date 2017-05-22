'''
    Qt/Objects/Threads/base
    _______________________

    Base class definitions shared by all threads in XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import abc
import traceback

from PySide import QtCore

from xldlib.qt import memo
from xldlib.qt.objects import base
from xldlib.utils import logger

from .mutex import ContextMutex

__all__ = [
    'BaseThread',
    'emit_error'
]

# MUTEX
# -----

MUTEX = ContextMutex('Recursive')


# DECORATORS
# ----------


def emit_error(error):
    '''Catch, log and emit error via `self.error`'''

    def decorator(f):
        def newf(self, *args, **kwds):
            try:
                return f(self, *args, **kwds)
            except error as err:
                trace = traceback.format_exc()
                logger.Logging.error(trace)

                self.error.emit(err)

        return newf
    return decorator


# THREADING
# ---------


@memo.thread
class BaseThread(QtCore.QThread, base.BaseObject):
    '''
    Base class for all QThreads within XL Discoverer. Provides weak
    memoization upon class initialization, and cleanup methods
    upon quitting.
    '''

    def __init__(self, parent=None):
        '''
        Args:
            parent (None, QtCore.QObject):  Qt parent for the thread
        '''
        super(BaseThread, self).__init__(parent)

        self._isrunning = False
        self.finished.connect(self.cleanup)

    #     PROPERTIES

    @property
    def isrunning(self):
        return self._isrunning

    @isrunning.setter
    def isrunning(self, value):
        self._isrunning = value

    #     PUBLIC

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    def cleanup(self):
        '''Close instance and remove instance memo upon finishing'''

        with MUTEX:
            self.quit()
            self.app.threads.pop(type(self).__name__, None)
