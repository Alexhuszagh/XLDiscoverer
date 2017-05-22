'''
    Qt/Objects/Threads/background
    _____________________________

    Background thread definition, which periodically emits signals
    during another thread's execution loop.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import time

from PySide import QtCore

from xldlib.qt import resources as qt
from xldlib.utils import logger

from . import base

__all__ = [
    'BackgroundThread'
]


# THREADING
# ---------


@logger.init('threading', 'DEBUG')
class BackgroundThread(base.BaseThread):
    '''
    Background thread to keep the GUI responsive during computationally
    intensive tasks in a worker class.

    The BackgroundThread instance emits a `self.update` signal every
    `self.sleep` seconds while `self.thread.isrunning`.
    '''

    # INTERVALS
    # ---------
    update = QtCore.Signal(bool)
    sleep = 0.01

    def __init__(self, thread, parent=None):
        super(BackgroundThread, self).__init__(parent)

        self.thread = thread
        thread.procedure_done.connect(self.cleanup, qt.CONNECTION['Queued'])

    @logger.call('threading', 'debug')
    @logger.except_error(RuntimeError)
    def run(self):
        '''Emit signals at time intervals while `worker.isrunning`'''

        self.isrunning = True
        while self.thread.isrunning:
            self.update.emit(True)
            time.sleep(self.sleep)

        self.isrunning = False
