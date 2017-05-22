'''
    Utils/IO_/spectra
    _________________

    Validates and loads spectral files if recognized as a PyTables object
    with a Python object wrapper.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os

import tables as tb

from xldlib import exception
from xldlib.objects import documents
from xldlib.utils import logger


# DATA
# ----

DOCUMENTS = {
    'transition': documents.TransitionsDocument
}

CACHE = {
    'transition': documents.TransitionsDocumentCache
}


# FUNCTIONS
# ---------


@logger.call('document', 'debug')
def load_file(path, fileformat, mode='a'):
    '''Validates and loads a spectral document'''

    try:
        cache = path + CACHE[fileformat].suffix
        assert os.path.exists(cache) and tb.is_pytables_file(cache)
        return DOCUMENTS[fileformat].open(path, mode=mode)

    except IOError:
        raise AssertionError(exception.CODES['013'])
    except (ValueError, AssertionError, KeyError):
        raise AssertionError(exception.CODES['023'])


@logger.except_error(Exception)
@logger.call('document', 'debug')
def write_file(document, path, indexes=None):
    '''Writes an open spectral document to file'''

    document.save(path, indexes)
