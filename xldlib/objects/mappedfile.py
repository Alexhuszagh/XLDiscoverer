'''
    Objects/mappedfile
    __________________

    Memory-mapped JSON-like file object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import atexit
import six

from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, serialization

__all__ = [
    'Data',
    'File'
]


# DATA
# ----


class Data(base.BaseObject):
    '''Definitions for an object wrapper for hierarchical data'''

    #     PUBLIC

    def __getattr__(self, name):
        '''
        Override __getattr__ to provide convenient `self.name` access
        to columns by column attribute names, otherwise, return
        class/instance variable.

        Args:
            name (str):  attribute name for column or class
        '''

        if self.__dict__.get('data') and name in self.data['attrs']:
            return self.data['attrs'][name]
        return super(Data, self).__getattribute__(name)

    def __setattr__(self, name, value):
        '''
        Override __setattr__ to provide convenient `self.name = value`
        access to columns by column attribute names, otherwise, return
        class/instance variable.

        Args:
            name (str):      attribute name for column or class
            value (object):  object to set
        '''

        if self.__dict__.get('data') and name in self.data['attrs']:
            self.data['attrs'][name] = value
        else:
            super(Data, self).__setattr__(name, value)

    #     PUBLIC

    def setattr(self, attr, value):
        self.data['attrs'][attr] = value

    def getattr(self, attr):
        return self.data['attrs'][attr]

    def hasattr(self, attr):
        return attr in self.data['attrs']

    def getattrs(self, attrs):
        return map(self.getattr, attrs)


# FILE
# ----


@serialization.register('MappedFile')
@logger.init('object', 'DEBUG')
class File(Data):
    '''Definitions for a spectral file'''

    # ATEXIT
    # ------
    _forcesave = True

    def __init__(self, path=None, data=None, registered=False):
        super(File, self).__init__()

        self.path = path
        self.data = data
        self.registered = registered

        if self._forcesave:
            atexit.register(self.save)

    #     MAGIC

    @serialization.tojson
    def __json__(self):
        '''Implementation to dump an object as a msgpack'''

        return {
            'path': self.path,
            'data': self.data
        }

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(**data)

    #     PUBLIC

    @classmethod
    @logger.call('object', 'debug')
    def new(cls, path=None, blank=False):
        '''Initialize file from template at `path`'''

        if path is None:
            path = cls._newpath()
        template = cls._new(blank)
        return cls(path, template, registered=True)

    @staticmethod
    @logger.call('object', 'debug')
    def open(path):
        '''Loads a File object from path'''

        pickling = defaults.DEFAULTS['enable_pickle']
        inst = serialization.deserialize(path, pickling)
        inst.registered = True

        return inst

    @classmethod
    @logger.call('object', 'debug')
    def tryopen(cls, path):
        '''Loads a File object from path'''

        try:
            return cls.open(path)
        except (IOError, OSError):
            return cls.new(path, blank=True)

    @logger.call('object', 'debug')
    def close(self):
        '''Closes the database to avoid pickling writes to file'''

        if six.PY3 and self._forcesave:
            # unregister undefined in PY2
            atexit.unregister(self.save)

        self.path = None
        self.data = None
        self.registered = False

    @logger.call('object', 'debug')
    def save(self, path=None, pickling=None):
        '''Saves the current object to File'''

        if path is None:
            path = self.path
        if pickling is None:
            pickling = defaults.DEFAULTS['enable_pickle']

        if self.registered:
            serialization.serialize(self, path, pickling)

    #   NON-PUBLIC

    @classmethod
    def _getpath(cls, path):
        '''Returns the normalized path from the query'''

        if path is None:
            path = cls._newpath()
        return path

    @staticmethod
    def _new(blank):
        return None

    @staticmethod
    def _newpath():
        return None
