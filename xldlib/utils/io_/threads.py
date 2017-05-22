'''
    Utils/IO_/threads
    _________________

    Thread which processes an I/O event passed as a frozen function.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import time

from xldlib.controllers import messages
from xldlib.qt.objects import threads
from xldlib.qt import resources as qt
from xldlib.utils import logger

# load objects/functions
from xldlib.definitions import partial


# THREADING
# ---------


@logger.init('gui', 'DEBUG')
class IoThreading(messages.BaseMessage):
    '''
    Provides methods to execute I/O events within a thread to keep
    the GUI responsive during long loading/saving events.
    '''

    def __init__(self, parent):
        '''
        Args:
            parent (QObject): Qt parent
        '''
        super(IoThreading, self).__init__()

        self.parent = parent

    def __call__(self, fun, dialog, *connects):
        '''
        Construct thread to process the I/O events and keep GUI responsive
        See `self._worker` for full arg specs.
        '''

        worker = self._worker(fun, dialog, connects)
        background = threads.BackgroundThread(worker, self)
        for thread in (worker, background):
            thread.start()

    #     PUBLIC

    def hide(self, dialog):
        '''
        Delay hide event on `dialog`  to avoid crash caused when the
        hideEvent occurs to close to the showEvent in the Qt library.

        Args:
            dialog (QDialog):   dialog updated by threading events
        '''

        time.sleep(0.1)
        dialog.hide()

    def error(self, message):
        '''
        Launch QMessageBox with `message` to report I/O errors

        Args:
            message (Exception, iterable):  Exception or error message
        '''

        if hasattr(message, "args") and len(message.args[0]) == 2:
            title, text = message.args[0]
            self.exec_msg(text=text, windowTitle=title)
        elif hasattr(message, "args"):
            self.exec_msg(text=message.args[0], windowTitle="Unknown error")
        else:
            title, text = message
            self.exec_msg(text=text, windowTitle=title)

    #   NON-PUBLIC

    def _worker(self, fun, dialog, connects):
        '''
        Initialize worker thread for I/O events.

        args:
            fun (callable):     function to execute within worker
            dialog (QDialog):   Widget kept responsive
            connects (tuple):   slots to connect to worker.finished
        '''

        worker = threads.WorkerThread(fun)

        hide = partial(self.hide, dialog)
        worker.finished.connect(hide, qt.CONNECTION['Queued'])
        worker.error.connect(self.error, qt.CONNECTION['Queued'])
        for connect in connects:
            worker.finished.connect(connect, qt.CONNECTION['Queued'])

        return worker
