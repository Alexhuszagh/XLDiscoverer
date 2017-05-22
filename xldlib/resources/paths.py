'''
    Resources/Other/paths
    _____________________

    Default paths for backing stores and configuration files.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import atexit
import os
import sys

from functools import reduce

from xldlib.definitions import partial
from xldlib.general import mapping


__all__ = [
    'DIRS',
    'FILES',
    'DYNAMIC'
]


# UTILS
# -----


def chain(f, n=1):
    '''
    Chain function calls

    Args:
        f (callable):   frozen callable
        n (int):        number if instances to chain the function
    '''

    return partial(reduce, (lambda x, y: y(x)), [f] * n)


def find_home():
    '''
    Find xldlib home directory from the current file

    Returns (str):  path to home directory
    '''

    if getattr(sys, 'frozen', False):
        origin = os.path.realpath(sys.executable)
        fun = chain(os.path.dirname, n=2)

    else:
        origin = os.path.realpath(__file__)
        fun = chain(os.path.dirname, n=3)

    return fun(origin)


def make_dirs(iterable):
    '''Make all non-existent paths specified in iterable'''

    for path in iterable:
        if not os.path.exists(path):
            os.makedirs(path)


# DIRS
# ----

HOME = find_home()
RESOURCE = os.path.join(HOME, 'resources')
BACKING_STORE = os.path.join(RESOURCE, 'backing_store')
DATA = os.path.join(RESOURCE, 'data')
DATABASES = os.path.join(RESOURCE, 'databases')
PREFERENCES = os.path.join(RESOURCE, 'preferences')

DIRS = {
    'home': HOME,
    'resource': RESOURCE,
    'backing_store': BACKING_STORE,
    'data': DATA,
    'databases': DATABASES,
    'preferences': PREFERENCES,
    'png': os.path.join(RESOURCE, 'png'),
    'views': os.path.join(PREFERENCES, 'views')
}

make_dirs(DIRS.values())


# FILES
# -----

FILES = {
    # logging
    'logger': os.path.join(HOME, '.xlDiscoverer.log'),

    # backing stores
    'spectra': os.path.join(BACKING_STORE, 'spectral_data.h5'),
    'matched': os.path.join(BACKING_STORE, 'discoverer_data.pkl'),
    'mowse': os.path.join(BACKING_STORE, 'mowse_data.h5'),
    'transition': os.path.join(BACKING_STORE, 'transition.xld'),
    'fingerprint': os.path.join(BACKING_STORE, 'fingerprint.pmf'),

    # spreadsheets
    'spreadsheet': os.path.join(DATA, 'xldiscoverer.xlsx'),
}


# CONFIGURABLE
# ------------

DYNAMIC_PATH = os.path.join(PREFERENCES, 'paths.json')

DYNAMIC = mapping.Configurations(DYNAMIC_PATH, [
    ('current_proteins', os.path.join(DATABASES, 'proteins.json'))
])

# REGISTERS
# ---------

atexit.register(DYNAMIC.save)
