'''
    Qt/Objects/Threads/mutex
    ________________________

    QMutex definition with a context manager.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore

from xldlib.qt import resources as qt

__all__ = [
    'ContextMutex'
]


# OBJECTS
# -------


class ContextMutex(QtCore.QMutex):
    '''
    QMutex with `__enter__` and `__exit__` methods to provide
    a full context manager.

    The Mutex locks using `self.locker` (default `QtCore.QMutex.lock`)
    '''

    def __init__(self, mode=QtCore.QMutex.NonRecursive, locker=None):
        '''
        Args:
            mode (str, QtCore.QMutex.RecursionMode): recursive mode for mutex
            locker (None, callable): callable to lock mutex
        '''
        super(ContextMutex, self).__init__(self.__modechecker(mode))

        if locker is None:
            locker = QtCore.QMutex.lock
        self.locker = locker

    #     MAGIC

    def __enter__(self):
        '''Enter locked state'''

        self.locker(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Exit locked state (do not except any errors)'''

        self.unlock()

    #    HELPERS

    def __modechecker(self, mode):
        '''Normalize QtCore.QMutex.RecursionMode types'''

        return qt.MUTEX_RECURSION.normalize(mode)
