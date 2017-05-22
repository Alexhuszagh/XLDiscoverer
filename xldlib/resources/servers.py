'''
    Resources/servers
    _________________

    Default server configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.definitions import re

__all__ = [
    'GIT_SERVER',
    'ID_REGEX',
    'MNEMONIC_REGEX'
]

# CONSTANTS
# ---------

ID = (r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]'
      r'([A-Z][A-Z0-9]{2}[0-9]){1,2}')
MNEMONIC = r'[a-zA-Z0-9]{1,5}_[a-zA-Z0-9]{1,5}'


# REGEXP
# ------

ID_REGEX = re.compile(ID, re.IGNORECASE)
MNEMONIC_REGEX = re.compile(MNEMONIC, re.IGNORECASE)


GIT_SERVER = {
    'domain': {
        'repos': 'repos',
        'tags': ['tags'],
        'releases': ['releases'],
        'assets': ['releases', 'assets'],
        'owner': 'Alexhuszagh',
        'repo': 'xlDiscoverer'
    },
    'protocol': 'https',
    'scheme': '://',
    'host': 'api.github.com',
    'path': '/',
    'at': '@',
    'port': 80
}
