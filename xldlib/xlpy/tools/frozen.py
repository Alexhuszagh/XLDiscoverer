'''
    Xlpy/Tools/frozen
    _________________

    Tools for freezing common data structures to give them a hash
    function.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import Counter, namedtuple

from xldlib.definitions import ZIP
from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.utils import logger, modtools


# DATA
# ----

CHARS = [
    'd',
    'u'
]


# OBJECTS
# -------


@sequence.serializable("XLIdentifier")
class XLIdentifier(namedtuple("XLIdentifier", "crosslinker number")):
    '''Serialization definitions'''


# MODIFICATIONS
# -------------


@logger.init('xlpy', 'DEBUG')
class ModificationFreezer(base.BaseObject):
    '''
    Converts internal data structures to enable hashing as applied
    to the mod dictionary, a nested dictionary with nested dictionaries
    and lists.
    '''

    def __init__(self, row, isobaric, ignoremodposition=False):
        super(ModificationFreezer, self).__init__()

        self.engine = row.engines['matched']
        self.isobaric = isobaric
        self.ignoremodposition = ignoremodposition

    def __call__(self, modification):
        '''Returns a frozen set representation of the mods'''

        tofreeze = list(self.getmodifications(modification))
        tofreeze.append(int(modification['neutralloss']))

        if self.ignoremodposition:
            return frozenset(Counter(tofreeze).items())
        else:
            return frozenset(tofreeze)

    #    GETTERS

    def getmodifications(self, modification):
        '''Returns unique identifiers for the certain and uncertain mods'''

        certain = modification['certain']
        uncertain = self.getuncertain(modification)
        for char, dicts in ZIP(CHARS, [[certain], uncertain]):
            for modificationdict in dicts:
                for name, positions in modificationdict.items():

                    # skip loop if not a standard modification
                    if name not in self.isobaric:
                        yield self.getmodstring(name, positions, char)

    def getuncertain(self, modification):
        '''Returns the uncertain list, or single element list'''

        if self.ignoremodposition:
            # grab slice of first item, works for null case too
            return modification['uncertain'][0:1]
        else:
            return modification['uncertain']

    def getmodstring(self, name, positions, char):
        '''
        Returns a string for the mod/position pair. Joins the positions
        as CSV-separated values.
            mod_string('Carbamidomethyl', [6, 12], 'u')
                ->'uCarbamidomethyl@6,12'
        '''

        if self.ignoremodposition:
            return name

        else:
            sortedpositions = sorted(positions, key=self.engine.key)
            positions = ','.join(str(i) for i in sortedpositions)
            return '{0}{1}@{2}'.format(char, name, positions)


# CROSSLINKS
# ----------


KEYS = (
    'modifications',
    'peptide',
    'id'
)


@logger.init('xlpy', 'DEBUG')
class SingleFreezer(base.BaseObject):
    '''Freezes a single link to render it unique based on identification'''

    def __init__(self, row, addindexes=False):
        super(SingleFreezer, self).__init__()

        self.row = row
        self.addindexes = addindexes

        source = self.app.discovererthread
        isobaric = source.parameters.isobaric.todict()
        self.modfreezer = ModificationFreezer(row, isobaric)

    def __call__(self, index, spreadsheet):
        '''Freeze the crosslinker attributes for set additions and lookups'''

        frozen = set()
        frozen.add(self.getmatched(index))
        frozen.add(XLIdentifier(None, None))
        frozen.add(tuple(sorted(spreadsheet['XL'])))

        if self.addindexes:
            frozen.add(tuple(sorted(index)))

        return frozenset(frozen)

    #    GETTERS

    def getmatched(self, index, keys=KEYS):
        '''Returns the unique matched data from the indexes'''

        row = self.row.data.getrow(index, keys, asdict=True)
        modification = self.modfreezer(row['modifications'])

        return frozenset((modification, row['peptide'], row['id']))


@logger.init('xlpy', 'DEBUG')
class CrosslinkFreezer(base.BaseObject):
    '''Freezes a crosslink to render it unique based on identification'''

    def __init__(self, row, crosslinker, addindexes=False):
        super(CrosslinkFreezer, self).__init__()

        self.row = row
        self.crosslinker = crosslinker
        self.addindexes = addindexes

        source = self.app.discovererthread
        isobaric = source.parameters.isobaric[crosslinker.id]

        self.modfreezer = ModificationFreezer(row, isobaric)
        self.fragment = modtools.FragmentPositions(row, isobaric)

    def __call__(self, indexes, ends):
        '''Freeze the crosslinker attributes for set additions and lookups'''

        frozen = set()
        frozen.add(tuple(sorted(self.getmatched(indexes))))
        frozen.add(XLIdentifier(self.crosslinker.id, ends.number))
        frozen.add(tuple(sorted(self.fragment(indexes))))

        if self.addindexes:
            frozen.add(tuple(sorted(indexes)))

        return frozenset(frozen)

    #    GETTERS

    def getmatched(self, indexes, keys=KEYS):
        '''Returns the unique matched data from the indexes'''

        for index in indexes:
            row = self.row.data.getrow(index, keys, asdict=True)
            modification = self.modfreezer(row['modifications'])

            yield frozenset((modification, row['peptide'], row['id']))


@logger.init('xlpy', 'DEBUG')
class LabeledCrosslinkFreezer(base.BaseObject):
    '''Freezes a crosslink to render it unique based on identification'''

    def __init__(self, row, isobaric):
        super(LabeledCrosslinkFreezer, self).__init__()

        self.row = row
        self.isobaric = isobaric

    @logger.call('xlpy', 'debug')
    def __call__(self, crosslink_index, states):
        '''Freezes the crosslinked-peptide attributes from the labels'''

        crosslink = self.__get_crosslink(crosslink_index)
        spreadsheet = self.__get_spreadsheet(crosslink_index)

        isobaric = self.isobaric[crosslink.crosslinker]
        modfreezer = ModificationFreezer(self.row, isobaric)

        modifications = states[0].modifications
        indexes = crosslink.index
        matched = self.getmatched(indexes, modifications, modfreezer)

        frozen = set()
        frozen.add(tuple(sorted(matched)))
        frozen.add(XLIdentifier(states[0].crosslinker, crosslink.ends.number))
        frozen.add(tuple(sorted(spreadsheet['XL'])))

        return frozenset(frozen)

    #  CLASS METHODS

    @classmethod
    def fromrow(cls, row):
        '''Initializes the class from a source thread'''

        source = cls.app.discovererthread
        isobaric = source.parameters.isobaric
        return cls(row, isobaric)

    #    GETTERS

    def getmatched(self, indexes, modifications, modfreezer):
        '''Returns the unique matched data from the indexes'''

        zipped = ZIP(modifications, indexes)
        for modification, index in zipped:
            modification = modfreezer(modification)
            peptide, uniprotid = self.row.data.getrow(index, ('peptide', 'id'))

            yield frozenset((modification, peptide, uniprotid))

    def __get_crosslink(self, crosslink_index):
        '''
        Returns the data indexes from the isotope-labeled crosslink
        Translates the index pointing to an unlabeled crosslink to
        one pointing at the matched data.
        '''

        return self.row.data['crosslinks'][crosslink_index]

    def __get_spreadsheet(self, crosslink_index):
        '''
        Returns the data indexes from the isotope-labeled crosslink
        Translates the index pointing to an unlabeled crosslink to
        one pointing at the matched data.
        '''

        return self.row.data['spreadsheet']['crosslinks'][crosslink_index]
