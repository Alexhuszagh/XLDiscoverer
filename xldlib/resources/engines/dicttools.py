'''
    Resources/Engines/dicttools
    ___________________________

    Dictionary definitions and methods for engines objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from functools import wraps

from xldlib.general import mapping
from xldlib.resources.parameters import defaults
from xldlib.utils.io_ import typechecker


# HELPERS
# -------


def read_header(f):
    '''
    Decorate function by passing fileobj header, determined by
    the `chunk_size` number of bytes, to the function.
    '''

    @wraps(f)
    def decorator(self, fileobj):
        with typechecker.seek_start(fileobj) as fileobj:
            header = fileobj.read(defaults.DEFAULTS['chunk_size'])
            if isinstance(header, bytes):
                header = header.decode('utf-8')
            return f(self, header)

    decorator.__name__ = f.__name__
    return decorator


# OBJECTS
# -------


@mapping.serializable("EngineDict")
class EngineDict(dict):
    '''Inheritable methods for engine objects'''

    #    PROPERTIES
#
#    @property
#    def fileformat(self):
#        return self._fileformat

    #     PUBLIC

    def iterengines(self, fileformat):
        '''Yield generator for all engines from a given file format'''

        #fileformat = self._fileformatchecker(fileformat)
        for name, versions in self.items():
            for version, engine in versions.items():
                if engine.format == fileformat:
                    yield (name, version, engine)

#    #     HELPERS
#
#    def _fileformatchecker(self, fileformat):
#        '''Normalize engine format types'''
#
#        if isinstance(fileformat, six.string_types):
#            return self.fileformat[fileformat]
#        return fileformat
