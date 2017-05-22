'''
    Objects/Documents/spectra
    _________________________

    Objects for processing and modifying loaded spectral documents
    (peptide mass fingerprinting and transition documents).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.gui.views.dialogs import export
from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.utils.io_ import qtio, spectra, threads

# load objects/functions
from xldlib.definitions import partial


# I/O
# ---


@logger.init('document', 'DEBUG')
class SpectraIo(base.BaseObject):
    '''Provides base methods for saving transitions and PMF files'''

    def __init__(self, parent):
        super(SpectraIo, self).__init__(parent)

        self.qt = self.parent()._qt
        self.threading = threads.IoThreading(self.parent())

        self.path = None

    #      I/O

    @logger.call('document', 'debug')
    def save(self):
        '''Saves the spectral document to file'''

        if self.path != self.parent()._qt['path']:
            self.parent().savedialog.show()
            self.app.processEvents()

            fun = partial(spectra.write_file,
                self.tree().document, self.path)
            self.threading(fun, self.parent().savedialog)
        else:
            self.saveas()

    @logger.call('document', 'debug')
    def saveas(self, indexes=None):
        '''Saves selected spectral files to a user-chosen path'''

        if indexes is None and self.tree().document is not None:
            indexes = range(len(self.tree().document))

        filepath = self._get_save_path('document_extension')
        if filepath:
            self.set_path(filepath, mode='replace')

            self.parent().savedialog.show()
            self.app.processEvents()

            fun = partial(spectra.write_file,
                self.tree().document, filepath, indexes)
            self.threading(fun, self.parent().savedialog)

    @logger.call('document', 'debug')
    def save_files(self):
        '''Saves specific files from the transitions list'''

        dialog = export.ExportDialog(self.tree().document,
            mode='save', parent=self.parent())
        dialog.show()

    @logger.call('document', 'debug')
    def save_spreadsheet(self, processor):
        '''Exports a spreadsheet using a custom processing function'''

        filepath = self._get_save_path('excel_extension')
        if filepath:
            self.parent().savedialog.show()
            self.app.processEvents()

            fun = partial(processor, self.tree().document, filepath)
            self.threading(fun, self.parent().savedialog)

    @logger.call('document', 'debug')
    def open(self, mode='replace'):
        '''adds or replaces spectral files to the document.'''

        title = self.__get_opentitle(mode)
        filepath = self._get_open_path('document_extension', title)
        if filepath:
            self.set_path(filepath, mode='replace')
            self.parent().loaddialog.show()
            self.app.processEvents()

            fun = self._get_openfun(filepath, mode)
            self.threading(fun, self.parent().loaddialog)

    @logger.call('document', 'debug')
    def save_image(self):
        '''Saves the currently displayed image'''

        filepath = self._get_save_path('image_extension', 'Save image as...')
        if filepath:
            self.canvas().save_image(filepath)

    @logger.call('document', 'debug')
    def close_selected_files(self):
        '''Finds which files to close'''

        dialog = export.ExportDialog(self.tree().document,
            mode='close', parent=self.parent())
        dialog.show()

    @logger.call('document', 'debug')
    def close_files(self, indexes=None):
        '''Closes files at each index, or all files (if indexes == None)'''

        if indexes is None:
            self.path = None
            self.tree().io.close_all_files()

        else:
            self.tree().io.close_selected_files(indexes)
            if self.tree().document is None:
                self.path = None

    #     SETTERS

    def set_path(self, path, mode):
        '''Sets the current path upon IO events'''

        if self.path is None or mode == 'replace':
            self.path = path

    #     GETTERS

    def _get_save_path(self, *args):
        return self._get_path(qtio.getsavefile, *args)

    def _get_open_path(self, *args):
        return self._get_path(qtio.getopenfile, *args)

    def _get_path(self, fun, suffix_key, title=qtio.SAVE_TITLE):
        '''Returns an openfile dialog with a given suffix filter'''

        suffix = self.qt[suffix_key]
        return fun(self.parent(), title, suffix=suffix)

    def _get_openfun(self, filepath, mode):
        '''Returns the file opening function for the document'''

        self.set_path(filepath, mode)
        if mode == 'add':
            return partial(self.tree().io.add_files, filepath)

        elif mode == 'replace':
            return partial(self.tree().io.open_files, filepath)

    @staticmethod
    def __get_opentitle(mode):
        '''Returns the QFileDialog title from the mode'''

        if mode == 'replace':
            return 'Open file...'
        elif mode == 'add':
            return 'Add files...'

    #     HELPERS

    def tree(self):
        return self.parent().widget.tree

    def canvas(self):
        return self.tree().visualizer_view.widget.canvas
