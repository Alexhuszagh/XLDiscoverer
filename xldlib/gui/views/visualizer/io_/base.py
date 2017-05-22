'''
    Gui/Views/Visualizer/IO_/base
    _____________________________

    Shared input/output methods for spectral documents.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os

from PySide import QtCore, QtGui

from xldlib.qt import resources as qt
from xldlib.utils import logger
from xldlib.utils.io_ import spectra

from .. import base, styles


# DECORATORS
# ----------


def disable_caching(f):
    '''
    Decorators which flanks a function to allow spectral document I/O
    with no in-memory array declarations, to avoid costly I/O events
    '''

    def decorator(self, document):
        document.memory = False
        if self.document is not None:
            self.document.memory = False

        result = f(self, document)

        document.memory = True
        self.document.memory = True

        return result

    decorator.__name__ = f.__name__
    return decorator



# I/O
# ---


@logger.init('document', 'DEBUG')
class BaseIo(base.DocumentChild):
    '''Inheritable methods for spectral I/O events'''

    def __init__(self, parent, fileformat):
        super(BaseIo, self).__init__(parent)

        self.fileformat = fileformat
        self.stylizer = styles.Stylizer(self.fileformat, parent)

    #  PUBLIC FUNCTIONS

    #      I/O

    @logger.call('document', 'debug')
    def add_files(self, path):
        '''Adds transitions to the QTreeView from a given file path.'''

        # read unless replacing file
        mode = 'r'
        if self._checknew():
            mode = 'a'

        document = spectra.load_file(path, self.fileformat, mode)
        if document is not None:
            self.add_document(document)

    @logger.call('document', 'debug')
    def open_files(self, path):
        '''Clears layout and adds transitions from a given file path.'''

        if self._checkpath(path, self.document):
            document = spectra.load_file(path, self.fileformat)
            if document is not None:
                self.close_all_files()
                self.add_document(document)

    @logger.call('document', 'debug')
    def close_all_files(self):
        '''Closes all open transition files'''

        if self.document is not None:
            self.clear()

            self.document.close()
            self.document = None

    @logger.call('document', 'debug')
    def close_selected_files(self, indexes):
        '''Closes files at the given indexes, generated form a QDialog'''

        if self.document is not None:
            for index in sorted(indexes, reverse=True):
                self.document.delete_file(index, reindex=False)

            self.document.reindex()
            self.document.save()

            self.clear()

            self.populate(self.document)

    #     DOCUMENTS

    @disable_caching
    def add_document(self, document):
        '''Adds the current transitions and associated files to the layout'''

        if self._checknew():
            self.__setnew(document)
            self.populate(document)

        else:
            self.checkattrs(document)

            row = len(self.document)
            self.__setfiles(document)
            document.close()
            self.document.save()

            # populate using the old rows
            self.populate(self.document[row:])

    @staticmethod
    def get_child(name, checkstate=True, size=qt.DEFAULT_SIZE):
        '''Makes a selectable, uneditable QChildWidget'''

        child = QtGui.QStandardItem(name, font=QtGui.QFont(size=size))
        if checkstate:
            child.setCheckState(QtCore.Qt.CheckState(True))
            child.setFlags(qt.ITEM['Selectable|UserCheckable|Enabled'])
        else:
            child.setCheckable(False)
        return child

    #     SETTERS

    def __setnew(self, document):
        '''Changes the current document to the loaded document'''

        self.document = document
        self.stylizer.setattrs()

    def __setfiles(self, newdocument):
        '''
        Adds the current files and sets the current file attributes if
        none currently exist.
        '''

        document = self.document
        row = len(document)
        for index, transitionfile in enumerate(newdocument):
            document.append(transitionfile)

            transitionfile.cache.copy(newparent=document.cache.root,
                newname=str(index + row),
                recursive=True)

    #     HELPERS

    def model(self):
        return self.parent().model

    def clear(self):
        self.model().deleteLater()
        self.parent().set_model()

    def _checkpath(self, path, document):
        '''Ensures the new path is not the same as the open document'''

        if document is not None:
            documentpath = os.path.realpath(path)
            return os.path.realpath(path) != documentpath
        else:
            return True

    def _checknew(self):
        return self.document is None
