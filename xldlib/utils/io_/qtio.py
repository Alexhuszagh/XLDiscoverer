'''
    Utils/IO_/qtio
    ______________

    Mapped functions and convenience functions for QtFileDialogs.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os

from PySide import QtGui

from xldlib.resources.parameters import defaults


# CONSTANTS
# ---------

SAVE_TITLE = 'Save File As... '
OPEN_TITLE = 'Open File...'

INPUT_KEY = 'input_directory'
OUTPUT_KEY = 'output_directory'


# FUNCTIONS
# ---------


def getpath(path, key):
    '''Returns a normalized path to pass as a parameter to a QFileDialog'''

    if path is None:
        path = defaults.DEFAULTS[key]
    return path


def storepath(path, key, isfile=True, store=True):
    '''Stores a filepath as a default directory for input data'''

    if isfile and path:
        path = os.path.dirname(path)

    if path and store:
        defaults.DEFAULTS[key] = path


def getfilters(suffix, ext='{0} files ({1})'):
    '''Returns the selected filters using the ";;" notation for Qt'''

    allfiles = "Any files (*)"
    if suffix is None:
        return allfiles, allfiles

    else:
        if isinstance(suffix.extension, (list, tuple)):
            extensions = ' '.join(['*.' + i for i in suffix.extension])
            string = ext.format(suffix.filetype, extensions)
        else:
            string = ext.format(suffix.filetype, '*.' + suffix.extension)
        return ';;'.join([string, allfiles]), string


def getwithextension(path, extension):
    '''
    Adds a default extension to a given filepath
    >>> getwithextension('path/to/file', Extension('HDF5', 'h5'))
        -> 'path/to/file.h5'
    >>> getwithextension('path/to/file.h5', Extension('HDF5', 'h5')')
        -> 'path/to/file.h5'

    >>> # doesn't override existing extensions
    >>> getwithextension('path/to/file.h4', Extension('HDF5', 'h5')')
        -> 'path/to/file.h4'
    '''

    ext = os.path.splitext(path)[1]
    if extension is not None and path and (not ext or len(ext) > 5):
        if isinstance(extension.extension, (list, tuple)):
            return path + '.' + extension.extension[0]
        else:
            return path + '.' + extension.extension
    return path


# EXPORT
# ------


def getsavefile(parent, title=SAVE_TITLE, path=None, suffix=None, store=True):
    '''Returns a save file name from a QFileDialog'''

    # get, save and store our path
    path = getpath(path, OUTPUT_KEY)
    filters, selected = getfilters(suffix)
    filepath = QtGui.QFileDialog.getSaveFileName(
        parent=parent,
        caption=title,
        dir=path,
        filter=filters,
        selectedFilter=selected)[0]

    filepath = getwithextension(filepath, suffix)
    storepath(filepath, OUTPUT_KEY, store=store)

    return filepath


# INPUT
# -----


def getopenfile(parent, title=OPEN_TITLE, path=None, suffix=None, store=True):
    '''Returns an open file name from a QFileDialog'''

    path = getpath(path, INPUT_KEY)
    filters, selected = getfilters(suffix)
    filepath = QtGui.QFileDialog.getOpenFileName(
        parent=parent,
        caption=title,
        dir=path,
        filter=filters,
        selectedFilter=selected)[0]

    storepath(filepath, INPUT_KEY, store=store)

    return filepath


def getopendir(parent, title, path=None):
    return QtGui.QFileDialog.getExistingDirectory(parent, title, path)
