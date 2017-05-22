'''
    Resources/version
    _______________________

    Versioning for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

_all__ = [
    'BUILD',
    'VERSION',
]

# VERSIONING
# ----------
MAJOR = 0
MINOR = 3
PATCH = 0
NIGHT_BUILD = ''

VERSION = '{0}.{1}.{2}'.format(MAJOR, MINOR, PATCH)
BUILD = VERSION + NIGHT_BUILD
