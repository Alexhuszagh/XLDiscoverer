'''
    Resources/Parameters/input_files
    ________________________________

    Holders for full paths to files for batch analysis

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os
import six

import tables as tb

from xldlib.general import mapping
from xldlib.resources import paths
from xldlib.utils import serialization


# PATHS
# -----

INPUT_FILE_PATH = os.path.join(paths.DIRS['data'], 'input_files.json')


# ENUMS
# -----

INPUT_FILE_TYPES = tb.Enum([
    'level_separated',
    'hierarchical'
])

CROSSLINK_DISCOVERER_MODES = tb.Enum([
    'default',
    'quantitative'
])


# OBJECTS
# -------


@serialization.register("InputFilesTable")
class InputFilesTable(mapping.TableModel):
    '''Definitions for input files'''

    # TABLE FACTORIES
    # ---------------
    __hierarchical = [
        ("MS Scans", "scans"),
        ("Matched Output", "matched")
    ]
    __default = [
        ("Precursor Scans", "precursor"),
        ("Product Scans", "product"),
        ("Matched Output", "matched")
    ]
    __quantitative = [
        ("Fullms Scans", "ms1"),
        ("Precursor Scans", "precursor"),
        ("Product Scans", "product"),
        ("Matched Output", "matched")
    ]

    def __init__(self, type_, mode, *args, **kwds):

        self.type = type_
        self.mode = mode
        keyorder = self.get_keyorder()

        super(InputFilesTable, self).__init__(keyorder)

        if args or kwds:
            self.__update(*args, **kwds)

    #      MAGIC

    def __reduce__(self):
        '''Adds pickling/unpickling support'''

        args = (self._type, self._mode)
        if six.PY2:
            return self.__class__, args, None, None, self.iteritems()
        else:
            return self.__class__, args, None, None, iter(self.items())

    @serialization.tojson
    def __json__(self):
        '''Implementation to dump an object as a msgpack'''

        return {
            'type': self._type,
            'mode': self._mode,
            'files': dict(self)
        }

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if isinstance(value, six.string_types):
            value = INPUT_FILE_TYPES[value]
        self._type = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if isinstance(value, six.string_types):
            value = CROSSLINK_DISCOVERER_MODES[value]
        self._mode = value

    @property
    def default(self):
        return self.mode == CROSSLINK_DISCOVERER_MODES['default']

    @property
    def hierarchical(self):
        return self.type == INPUT_FILE_TYPES['hierarchical']

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(data['type'], data['mode'], data['files'])

    #     GETTERS

    def get_keyorder(self):
        '''Sets the only keys allow in the table'''

        if self.hierarchical:
            return self.__hierarchical
        elif self.default:
            return self.__default
        else:
            return self.__quantitative

    #     HELPERS

    def _match(self, row, column, search):
        '''Checks if a search query matches the item at the cell'''

        value = self.list[column][row]
        count = len(search.findall(value))
        return os.path.basename(value), count

    def _replace(self, row, column, search, repl):
        '''Checks and replaces the item if it matches the query'''

        value = self.list[column][row]
        value = search.sub(repl, value)
        self.list[column][row] = value

        return value

    __update = mapping.update_setitem


class InputFileMode(dict):
    '''Dict with set properties for a specific submode of the input files'''

    #   PROPERTIES

    @property
    def current(self):
        return self['current']

    @current.setter
    def current(self, value):
        self['current'] = value

    @property
    def level_separated(self):
        return self.current == 'level_separated'

    @property
    def hierarchical(self):
        return self.current == 'hierarchical'

    @property
    def current_table(self):
        return self[self.current]


class InputFileConfigurations(mapping.IoMapping):
    '''Creates a mapping structure with all the input file types'''

    def __init__(self, path=INPUT_FILE_PATH):
        super(InputFileConfigurations, self).__init__()

        self._set_template()

        self.path = path
        self.ioload()

    #     SETTERS

    def _set_template(self):
        '''Sets a default template for the input files'''

        for mode in CROSSLINK_DISCOVERER_MODES._names:
            self[mode] = input_files = InputFileMode()
            input_files.current = 'level_separated'

            for type_ in INPUT_FILE_TYPES._names:
                input_files[type_] = InputFilesTable(type_, mode)

    #     GETTERS

    def get_table(self, enum):
        '''Returns a subtable from the FrozenTable'''

        if isinstance(enum, six.integer_types):
            enum = CROSSLINK_DISCOVERER_MODES(enum)
        elif isinstance(enum, bool):
            enum = CROSSLINK_DISCOVERER_MODES(int(enum))
        return self[enum]

    #      I/O

    def ioload(self):
        '''Loads the changed configurations from file'''

        document = self._ioload()
        if document is not None:
            self.update_mapping(document)


INPUT_FILES = InputFileConfigurations()
