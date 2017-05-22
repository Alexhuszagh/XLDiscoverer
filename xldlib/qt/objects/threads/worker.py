'''
    Qt/Objects/Threads/worker
    _________________________

    Generic worker thread which processes a frozen function within
    a thread loop.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import time

from PySide import QtCore

from xldlib.utils import logger

from . import base


__all__ = [
    'WorkerThread'
]


# OBJECTS
# -------


@logger.init('threading', 'DEBUG')
class WorkerThread(base.BaseThread):
    '''
    Generalized worker thread, which calls a frozen function
    within the thread execution.

    `WorkerThread.procedure_done` emits a signal prior to
    `WorkerThread.finished`, allowing early cleanup.

    `WorkerThread.error` allows custom error handling outside the
    thread loop, allowing normal thread termination

    `WorkerThread.result` allows the return object from the frozen
    function to be returned to the calling thread.
    '''

    # SIGNALS
    # -------
    procedure_done = QtCore.Signal(bool)
    error = QtCore.Signal(object)
    result = QtCore.Signal((object,), (int,), (str,))

    def __init__(self, fun, parent=None):
        '''
        Args:
            fun (function): frozen function to execute within `run` loop
            parent (None, QObject): Qt parent
        '''
        super(WorkerThread, self).__init__(parent)

        self.fun = fun

    #     PUBLIC

    def run(self):
        '''Initialize thread'''

        self.isrunning = True
        self._start()

        self.isrunning = False
        self.procedure_done.emit(True)
        time.sleep(0.1)

    #   NON-PUBLIC

    @base.emit_error(Exception)
    def _start(self):
        '''Non-public function to catch errors from the function call'''

        result = self.fun()
        if result is not None:
            self.result.emit(result)
