'''
    Resources/Chemical_Defs/interactions
    ____________________________________

    Interactions between post-translational modifications,
    such as how Label:15N(2)+Deamidation becomes a net 15N-1 H-1 O1,
    or a mass change of 0.13 Da, rather than N-1 H-1 O1.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import ast
import os

from xldlib.definitions import Json
from xldlib.general import mapping
from xldlib.resources import paths
from xldlib.utils import serialization


# load objects/functions
from namedlist import namedlist


# PATHS
# -----
INTERACTIONS_PATH = os.path.join(paths.DIRS['data'], 'interactions.json')


# OBJECTS
# -------

Interaction = namedlist("Interaction", "names converted")


@serialization.register('InteractionsStorage')
class InteractionsStorage(mapping.IoMapping):
    '''
    Stores modification interactions in a simple mapping structure with
    sorted tuple keys, which then are dumped as strings and re-evauated on
    load.
    '''

    __update = dict.update

    def __init__(self, path, defaults):
        super(InteractionsStorage, self).__init__()

        self.__update(defaults)
        self.path = path
        self.changed = {}

        self.ioload()

    #      MAGIC

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''Type converts all new values -- keys must exist in defaults'''

        value = self._interactionchecker(value)
        self.changed[key] = value
        dict_setitem(self, key, value)

    #      I/O

    def ioload(self):
        '''Loads the changed configurations from file'''

        document = self._ioload()
        if document is not None:
            document = self.__newdocument(document)
            self.update(document)

    def save(self):
        '''Dumps the JSON configurations to file'''

        changed = {str(set(k)): v for k, v in self.changed.items()}
        with open(self.path, "w") as dump:
            Json.dump(changed, dump, sort_keys=True, indent=4,
                default=configurations.tojson)

    #    PUBLIC

    update = mapping.update_setitem

    #     HELPERS

    def _interactionchecker(self, item):
        '''Returns a Interaction instance from the item'''

        if isinstance(item, Interaction):
            return item

        elif isinstance(item, (list, tuple)) and len(item) == 2:
            return Interaction(*item)

        else:
            raise AssertionError("Modification Interaction not recognized")

    def __newdocument(self, document):
        '''Returns a new, fixed document with the built-in types'''

        newdocument = {}
        for key, value in document.items():
            key = frozenset(ast.literal_eval(k))
            value = self._interactionchecker(value)

            newdocument[key] = value
        return newdocument


# DATA
# ----


MODIFICATION_INTERACTIONS = InteractionsStorage(INTERACTIONS_PATH, [
    (frozenset({'Deamidated', 'Label:15N(2)'}), Interaction(
        names=['Deamidated', 'Label:15N(2)'],
        converted=146))
])
