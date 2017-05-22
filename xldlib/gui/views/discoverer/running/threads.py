'''
    Gui/Views/Crosslink_Discoverer/Running/threads
    ______________________________________________

    Thread controller for the RunLinkDiscoverer QDialog

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.gui.views.windows import transition
from xldlib.qt.objects import base
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import close


# THREAD HANDLERS
# ---------------


@logger.init('threading', 'DEBUG')
class ThreadHandler(base.BaseObject):
    '''Object to help facilitate thread handling outside the GUI loop'''

    def __init__(self, parent):
        super(ThreadHandler, self).__init__(parent)

        self._paused = False

    #    PROPERTIES

    @property
    def worker(self):
        return self.parent().worker

    @property
    def background(self):
        return self.parent().background

    # PUBLIC FUNCTIONS

    def fin(self):
        '''Closes the threads upon the end of the threading event'''

    def pause(self, mode):
        '''Pauses the worker thread'''

        if mode == 'transition':
            self.launch_transition()
        elif mode == 'fingerprint':
            self.launch_fingerprint()

    def unpause(self, mode):
        '''Unpauses the worker thread'''

        # show the windowsef fin
        self.parent().show()
        self.app.discovererwindow.show()

        self.app.setOverrideCursor(qt.CURSOR['Wait'])
        self.worker.unpause(mode)

    #    LAUNCHERS

    def launch_transition(self):
        '''Launches the transition window'''

        condition = qt_config.TRANSITIONS['launch']
        cls = transition.TransitionWindow
        document = self.worker.transitions
        self._launch(condition, cls, document)

    def launch_fingerprint(self):
        '''Launches the peptide mass fingerprint window'''

        #condition = qt_config.FINGERPRINT['launch']
        #cls = transition.TransitionWindow
        #document = self.worker.transitions
        #self._launch(condition, cls, document)

    def _launch(self, condition, cls, document):
        '''Launcher for document editors'''

        if condition:
            self.reset_cursor()
            cls(document, self)

            # hide the windows
            self.parent().hide()
            self.app.discovererwindow.hide()

        else:
            self.unpause()

    #     HELPERS

    def reset_cursor(self):
        self.app.setOverrideCursor(qt.CURSOR['Arrow'])

    def close(self):
        '''Closes the threads on an error or closeEvent'''

        self.worker.isrunning = False
        if hasattr(self.worker, "protein_model"):
            del self.worker.protein_model
        self.close_documents()

        for thread in self.parent().threads:
            try:
                thread.isrunning = False
                thread.quit()
            except RuntimeError:
                # already deleted
                pass

        # need to turn off running on main_frame, so it can close
        # without the QDialog
        self.app.discovererwindow.isrunning = False

    def close_documents(self):
        '''Closes all open documents explicitly on the closeEvent'''

        self.worker.rundata.close()
        self.worker.matched.close()
        self.worker.proteins.close()

        if self.worker.quantitative:
            self.worker.transitions.close(save=False)

    @logger.call('threading', 'debug')
    def check_close_event(self, event):
        '''
        Processes the close event to see if Xl Discoverer is running,
        in order to not disrupt calculations.
        '''

        if self.worker.isrunning:
            # use a QDialog asking if the user really wants to quit
            close.running_closeevent(event)
            if not event.isAccepted():
                return False
        else:
            # if running is over, accept the closeEvent
            event.accept()

        return True
