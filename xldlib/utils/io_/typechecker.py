'''
    Utils/Io_/typechecker
    _____________________

    Type checkers for spectral filetypes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import contextlib
import tarfile
import zipfile

from functools import wraps

import six

import tables as tb

from xldlib import resources
from xldlib.definitions import re


__all__ = [
    'bzip2',
    'gz',
    'hdf5',
    'mime',
    'pkzip',
    'raw',
    'seek_start',
    'sqlite',
    'tar',
    'xml',
]

# REGEX
# -----

XML_DECLARATION = re.compile(r'<\?xml version="\d\.\d" encoding=".+"\?>\r?\n')
XML_FORMAT = re.compile(r'^\s*<\w+ xmlns=')
MIME_DELARATION = re.compile('MIME-Version: .+')


# HELPERS
# -------


@contextlib.contextmanager
def seek_start(fileobj):
    '''
    Context manager which seeks the fileobj start,
    yields the fileobj, and then re-seeks the object
    start to allow sequential reads for file-format
    determination to leave the fileobj start position
    unchanged.
    '''

    try:
        fileobj.seek(0)
        yield fileobj
    finally:
        fileobj.seek(0)


def file_handle(f, close_new=True):
    '''
    Function decorator for `f` which passes an open file handle
    to the function, from either a path or a file handle.
    '''

    @wraps(f)
    def decorator(fileobj):
        '''
        Args:
            fileobj (str, buffer):  Normalize file handle
        '''

        with _filechecker(fileobj, close_new) as fileobj:
            return f(fileobj)

    return decorator


def path_handle(f):
    '''
    Function decorator for `f` which passes a file path
    to the function, from either a path or a file handle.
    '''

    @wraps(f)
    def decorator(path):
        '''
        Args:
            path (str, buffer):  Normalize path to file
        '''

        with _pathchecker(path) as path:
            return f(path)

    return decorator


# BINARY TYPES
# ------------


@file_handle
def raw(fileobj):
    '''Return file object is Thermo Finnigan Raw file'''

    return _read_header(fileobj, 'RAW')


@path_handle
def hdf5(path):
    '''Return path to file object is HDF5'''

    return tb.is_hdf5_file(path)


@file_handle
def sqlite(fileobj):
    '''
    Return file object is SQLite(3). Due to the presence of bad
    continuation elements for the SQLite file format, open the file
    in binary mode..
    '''

    return _read_header(fileobj, 'SQLite3')


@file_handle
def gz(fileobj):
    '''Return fileobj is gzip-compressed'''

    return _read_header(fileobj, 'gz')


@path_handle
def pkzip(path):
    '''Return path points to a PK-zip archive'''

    return zipfile.is_zipfile(path)


@file_handle
def bzip2(fileobj):
    '''Return fileobj is bz2-compressed'''

    return _read_header(fileobj, 'bz2')


@path_handle
def tar(path):
    '''Return path points to a tarfile archive'''

    return tarfile.is_tarfile(path)


# TEXT TYPES
# ----------


@file_handle
def xml(fileobj):
    '''
    Return fileobj is XML. Checks first line for an XML declaration,
    and failing that, looks for an XML schema specified by the `xlmns`
    tag.
    '''

    with seek_start(fileobj) as fileobj:
        line = _decoded(fileobj.readline())
        if XML_DECLARATION.match(line):
            return True
        else:
            return bool(XML_FORMAT.match(line))


@file_handle
def mime(fileobj):
    '''Return file object is MIME data type'''

    with seek_start(fileobj) as fileobj:
        line = _decoded(fileobj.readline())
        return bool(MIME_DELARATION.match(line))


# PRIVATE
# -------


@contextlib.contextmanager
def _filechecker(fileobj, close_new):
    '''Normalize file object handles'''

    try:
        opened = False
        if isinstance(fileobj, six.string_types):
            fileobj = open(fileobj, 'rb')
            opened = True
        yield fileobj

    finally:
        if close_new and opened:
            fileobj.close()


@contextlib.contextmanager
def _pathchecker(path):
    '''Normalize file paths'''

    if hasattr(path, "read") and hasattr(path, "name"):
        # file object-like, buffer of path on file
        path = path.name
    yield path


def _decoded(string, encoding='utf-8'):
    '''Decode `string` to `encoding`'''

    if six.PY3 and isinstance(string, bytes):
        return string.decode(encoding)
    return string


def _read_header(fileobj, key):
    '''
    Check if the file object matches a given file format
    by reading the header and comparing it to the expected
    header specified by the `key`.

    Args:
        fileobj:    open file handle
        key (str):  key to BINARY_FILES
    '''

    header = resources.BINARY_FILES[key].header
    with seek_start(fileobj) as fileobj:
        return header == fileobj.read(len(header))
