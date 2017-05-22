'''
    XlPy/Tools/Modtools/positions
    _____________________________

    Tools to extract and and weight post-translational modification
    positions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six

from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.utils import logger


# STANDARD POSITIONS
# ------------------


@logger.init('modifications', 'DEBUG')
class ResidueFinder(base.BaseObject):
    '''
    Returns the residue from a peptide and position based on the engine
    and crosslinker settings
    '''

    def __init__(self, row, crosslinker):
        super(ResidueFinder, self).__init__()

        self.endsites = set(crosslinker.ends.aminoacid)

        engine = row.engines['matched']
        self.nterm = engine.defaults.nterm
        self.cterm = engine.defaults.cterm

    def __call__(self, peptide, position):
        '''Returns the normalized residue from the modification site'''

        if position == self.nterm and peptide[0] not in self.endsites:
            # nterm == free amine, lysine-like
            return 'K'
        elif position == self.nterm:
            return peptide[0]
        elif position == self.cterm and peptide[-1] not in self.endsites:
            # cterm == free carboxylate, aspartate-like
            return 'D'
        elif position == self.cterm:
            return peptide[-1]
        else:
            # otherwise, index it normally, removing the 1-index
            return peptide[position - 1]


# CROSSLINKER POSITIONS
# ---------------------


@logger.init('modifications', 'DEBUG')
class FragmentPositions(base.BaseObject):
    '''
    Makes the XL format for the crosslink reports. Adjusts for
    1-indexing.
    '''

    def __init__(self, row, isobaric):
        super(FragmentPositions, self).__init__()

        self.row = row
        self.engine = row.engines['matched']
        self.isobaric = isobaric

    def __call__(self, indexes, keys=('modifications', 'peptide', 'start')):
        '''list(FragmentPositions()) -> ['K37;K41;K42', 'K58']'''

        for index in indexes:
            values = self.row.data.getrow(index, keys)
            yield ';'.join(self.getcrosslinkpositions(*values))

    #    GETTERS

    def getcrosslinkpositions(self, modification, *args):
        '''
        Grabs the crosslinker positions from the index in the data holder
            -> ['K37', 'K41', 'K42']
        '''

        positions = self.getcertain(modification, *args)
        uncertain = self.getuncertain(modification, *args)
        if uncertain:
            positions.append(uncertain)

        return positions

    def getcertain(self, modification, *args):
        '''Gets the fragment positions from the certain mods'''

        certain = modification['certain']
        positions = list(self.getextracted(certain, *args))
        positions.sort(key=self.sortkey)
        return [''.join(str(i) for i in item) for item in positions]

    def getuncertain(self, modification, *args):
        '''Gets the fragment positions from the uncertain mod combinations'''

        uncertain = self.getuncertainpositions(modification, *args)
        groupsort = (sorted(i, key=self.sortkey) for i in uncertain)
        filtered = (i for i in groupsort if i)
        allsorted = sorted(filtered, key=self.customkey)
        joined = ('&'.join(i) for i in self.getuncertainjoined(allsorted))
        return '|'.join(sequence.uniquer(joined))

    def getuncertainpositions(self, modification, *args):
        '''Returns the uncertain positions for the crosslinked peptide'''

        for uncertain in modification['uncertain']:
            yield self.getextracted(uncertain, *args)

    def getuncertainjoined(self, uncertain):
        '''Returns the joined uncertain positions within the generator'''

        for positions in uncertain:
            yield (''.join(str(i) for i in item) for item in positions)

    # POSITION EXTRACTION

    def getextracted(self, modification_dict, *args):
        '''
        Unpacks mod dictionary to '{}@{}'.format(name, pos)
        list of strings.
        '''

        for name, positions in modification_dict.items():
            # only continue if a cross-linker modification
            if name in self.isobaric:
                for position in positions:
                    yield self.getposition(position, *args)

    def getposition(self, position, peptide, start):
        '''Processes mod position and adds modifying residue.'''

        if isinstance(position, six.integer_types):
            # adjust for 1-indexing
            residue = peptide[position - 1]
            position = position + start - 1

        elif position == self.engine.defaults.nterm:
            # add ':' to separate strings
            residue = peptide[0] + ':'

        elif position == self.engine.defaults.cterm:
            residue = peptide[-1] + ':'

        return residue, position

    #    SORTING

    def sortkey(self, item):
        '''('K', 124) -> 124'''

        return self.engine.key(item[1])

    def customkey(self, item):
        '''[('K', 124)] -> 124'''

        return self.engine.key(item[0][1])
