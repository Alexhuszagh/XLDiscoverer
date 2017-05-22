'''
    Gui/Views/Crosslink_Discoverer/io_
    __________________________________

    I/O controller for the RunLinkDiscoverer QDialog

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import shutil

from xldlib.definitions import partial
from xldlib.gui.views.dialogs import save
from xldlib.qt.objects import views
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources import paths
from xldlib.utils import logger
from xldlib.utils.io_ import qtio, spectra, threads


# I/O HANDLERS
# ------------


@logger.init('gui', 'DEBUG')
class IoHandler(views.BaseView):
    '''Object to help facilitate I/O events outside of the GUI loop'''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER

    def __init__(self, parent):
        super(IoHandler, self).__init__(parent)

        self.savedialog = save.IoDialog(parent=self.parent())
        self.threading = threads.IoThreading(self.parent())

    #     PROPERTIES

    @property
    def worker(self):
        return self.parent().worker

    #     PUBLIC

    @logger.call('gui', 'debug')
    def session(self, suffix=None):
        '''Saves the session data via a shutil copy'''

        if suffix is None:
            suffix = self.qt['session_extension']
        self._save(self._session, suffix)

    @logger.call('gui', 'debug')
    def excel(self, suffix=None):
        '''Saves the Excel spreadsheet via a shutil copy'''

        if suffix is None:
            suffix = self.qt['excel_extension']
        self._save(self._excel, suffix)

    @logger.call('gui', 'debug')
    def transitions(self, suffix=None):
        '''Saves the transitions PyTables file via a shutil copy'''

        if suffix is None:
            suffix = self.qt['transitions_extension']

        condition = os.path.exists(paths.FILES['transition'])
        self._save(self._transitions, suffix, condition)

    @logger.call('gui', 'debug')
    def fingerprint(self, suffix=None):
        '''Saves the PMF PyTables file via a shutil copy'''

        if suffix is None:
            suffix = self.qt['fingerprint_extension']

        condition = os.path.exists(paths.FILES['fingerprint'])
        self._save(self._transitions, suffix, condition)

    #    PRIVATE

    def _save(self, fun, suffix, condition=True):
        '''Connects the QFileDialog to a save method if a path selected'''

        filepath = qtio.getsavefile(self.parent(), suffix=suffix)
        if filepath and condition:
            self.savedialog.show()
            self.parent().app.processEvents()

            fun(filepath)

    def _session(self, filepath):
        '''Save function for session data'''

        fun = partial(self.worker.matched.save, filepath)
        self.threading(fun, self.savedialog)

    def _excel(self, filepath):
        '''Save function for Open Office spreadsheets'''

        fun = partial(shutil.copy, paths.FILES['spreadsheet'], filepath)
        self.threading(fun, self.savedialog)

    def _transitions(self, filepath):
        '''Save function for Transitions documents'''

        document = self.worker.transitions
        indexes = range(len(document))
        fun = partial(spectra.write_file, document, filepath, indexes)
        self.threading(fun, self.savedialog)

    def _fingerprint(self, filepath):
        '''Save function for Fingerprint documents'''

        raise NotImplementedError
