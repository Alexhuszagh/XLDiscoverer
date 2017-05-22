'''
    Exceptions/classes
    __________________

    Custom exception classes

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''


__all__ = [
    'ModificationError',
]


# EXCEPTIONS
# ----------


class ModificationError(Exception):
    '''
    Custom exception for errors during the parsing of
    post-translational modifications. Using classes derived
    from this error facilitate detection and processing
    of post-translation modifications.
    '''

    def __init__(self, message="Cannot parse the modification "):
        super(ModificationError, self).__init__(message)
