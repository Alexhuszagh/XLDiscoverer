'''
    Utils/IO_/ziptools
    __________________

    Methods for extracting/compressing zip archives and cleaning
    up temporary files.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import bz2
import gzip
import os
import shutil
import tarfile
import zipfile

from . import high_level, typechecker

__all__ = [
    'decompress'
]


# PUBLIC
# ------


@typechecker.file_handle
def decompress(fileobj, close_new=True):
    '''
    Determine if file object is a compressed, and decompress
    the file, returning an open file handle to the unzipped
    object.

    Supported file formats:
        .gz -- gunzip
        .tar(.gz) -- tarballs
        .zip -- Windows zipped
        .bz2 -- bzip2
    '''

    if typechecker.pkzip(fileobj.name):
        return _extract_zipfile(fileobj.name)
    elif typechecker.tar(fileobj.name):
        return _extract_tarball(fileobj.name)
    elif typechecker.gz(fileobj):
        return _extract_gzip(fileobj)
    elif typechecker.bzip2(fileobj):
        return _extract_bzip2(fileobj)
    return fileobj


# PRIVATE
# -------


def _extract_zipfile(path):
    '''
    Extract file object from a PK zipfile archive at `path`
    Args:
        path (str):     path to archive
    '''

    archive = zipfile.ZipFile(path)

    # need to ensure only single entry and is a file (not a dir)
    names = archive.namelist()
    name = names[0]
    assert len(names) == 1 and name[-1] != '/'

    # extract single file and return fileobj
    archive.extract(name, path=high_level.TMP_DIR)
    archive.close()
    return _new_fileobj(name)


def _extract_tarball(path):
    '''
    Extract file object from tarball at `path`
    Args:
        path (str):     path to archive
    '''

    archive = tarfile.open(path)

    # need to ensure only single entry and is a file (not a dir)
    names = archive.getnames()
    name = names[0]
    assert len(names) == 1 and name[-1] != '/'

    # extract single file and return fileobj
    archive.extract(name, path=high_level.TMP_DIR)
    archive.close()
    return _new_fileobj(name)


def _extract_gzip(fileobj):
    '''
    Extract gzip archive. The object is extracted to file to avoid
    holding the entire buffer in memory at once.
    Args:
        fileobj (buffer):     open file handle in 'rb' mode
    '''

    name = high_level.mkstemp()
    with open(name, 'wb') as dest:
        # fileobj must be passed in 'rb' mode
        with gzip.GzipFile(fileobj=fileobj, mode='rb') as src:
            shutil.copyfileobj(src, dest)

    return open(name, 'rb')


def _extract_bzip2(fileobj):
    '''
    Extract bzip2 archive.  The object is extracted to file to avoid
    holding the entire buffer in memory at once.
    '''

    name = high_level.mkstemp()
    with open(name, 'wb') as dest:
        with bz2.BZ2File(fileobj.name, mode='rb') as src:
            shutil.copyfileobj(src, dest)

    return open(name, 'rb')


def _new_fileobj(name, tmp_dir=high_level.TMP_DIR):
    '''
    Move extracted file to the temp dir and return open handle.
    Args:
        name (str):     extracted file object name (in tmp_dir)
        tmp_dir (str):  path `/tmp` or other temporary file dir
    '''

    src = os.path.join(tmp_dir, name)
    tempname = high_level.mkstemp()
    dst = os.path.join(tmp_dir, tempname)

    shutil.move(src, dst)

    return open(dst, 'rb')
