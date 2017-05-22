'''
    Resources
    _________

    Resource definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .binary import *
from .contact import *
from .isotopic_labels import *
from .messages import *
from .scan_titles import SCAN_TITLES
from .servers import *
from .species import *
from .version import *

__all__ = [
    'ABRIDGED_LICENSE',
    'AUTHOR',
    'AUTHOR_EMAIL',
    'BINARY_FILES',
    'BUILD',
    'GIT_SERVER',
    'ID_REGEX',
    'ISOTOPIC_LABELS',
    'MAINTAINER',
    'MAINTAINER_EMAIL',
    'MESSAGES',
    'MNEMONIC_REGEX',
    'SCAN_TITLES',
    'TAXA',
    'VERSION',
]
