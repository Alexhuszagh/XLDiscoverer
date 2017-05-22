'''
    Objects/Chemical/isobaric
    _________________________

    Runtime parameters for main thread, which can be reconstructed
    from the run dataset.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import defaultdict, namedtuple

from xldlib import chemical
from xldlib.utils import logger, serialization

# OBJECTS
# -------

Reactivity = namedtuple("Reactivitiy", "positions terminus")


# HELPERS
# -------


def getfragments(crosslinkers, modifications):
    '''Complete crosslinker fragment lookup table'''

    fragments = {}
    for crosslinkerid, crosslinker in crosslinkers.items():
        items = [modifications[i] for i in crosslinker.fragments]
        fragments[crosslinkerid] = items
    return fragments


def getspecificity(fragment, precision=3):
    '''Returns the fragment rounded mass and reactivity'''

    formula_ = chemical.Molecule(fragment.formula)
    mass = round(formula_, precision)

    positions = fragment.aminoacid.split(',')
    reactivity = [Reactivity(i, fragment.terminus) for i in positions]

    return mass, reactivity


def getmasses(fragments, crosslinkerid, crosslinkers):
    '''Returns the masses list with residue-mapped ID'''

    masses = defaultdict(set)

    for fragment in fragments[crosslinkerid]:
        mass, reactivity = getspecificity(fragment)
        masses[mass].update(reactivity)

    return masses


def getnames(fragments, crosslinkerid):
    '''Generates a name mapping structure for the framents'''

    names = CrosslinkerIsobaric()
    for fragment in fragments[crosslinkerid]:
        names[fragment.name].append(fragment)
    return names


def getallnames(fragments, crosslinkers, crosslinkerid):
    '''
    Checks similar reactivity and creates quick O(1) lookup table
    for a particular crosslinker ID to all fragments.
    '''

    names = getnames(fragments, crosslinkerid)
    masses = getmasses(fragments, crosslinkerid, crosslinkers)

    # add the isobaric modifications
    otherids = (i for i in crosslinkers if i != crosslinkerid)
    for otherid in otherids:
        for fragment in fragments[otherid]:

            # check if they have the same mass and can co-habitate
            # the same modification
            mass, reactivity = getspecificity(fragment)
            if any(i in masses.get(mass, {}) for i in reactivity):
                names[fragment.name].append(fragment)
    return names


def getisobaric(crosslinkers, fragments):
    '''Generates a lookup table by fragment name for isobaric crosslinkers'''

    isobaric = {}
    for crosslinkerid in crosslinkers:
        names = getallnames(fragments, crosslinkers, crosslinkerid)
        isobaric[crosslinkerid] = names
    return isobaric


# ISOBARIC
# --------


@serialization.register('CrosslinkerIsobaric')
@logger.init('chemical', 'DEBUG')
class CrosslinkerIsobaric(defaultdict):
    '''Definitions for isobaric modifications from a single crosslinker'''

    def __init__(self, factory=list, *args, **kwds):
        super(CrosslinkerIsobaric, self).__init__(factory, *args, **kwds)

    #      MAGIC

    @serialization.tojson
    def __json__(self):
        return dict(self)

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(list, data)

    #     PUBLIC

    def containsfragments(self, modification):
        '''Determines whether to modification contains any fragments'''

        if hasattr(modification, "unpack"):
            modification = modification.unpack()
        return any(modname in self for modname in modification)


@serialization.register('Isobaric')
@logger.init('chemical', 'DEBUG')
class Isobaric(dict):
    '''Contains settings for storing isobaric crosslinker modifications'''

    def __init__(self, isobaric):
        super(Isobaric, self).__init__(isobaric)

    #      MAGIC

    @serialization.tojson
    def __json__(self):
        return dict(self)

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(data)

    @classmethod
    def new(cls, crosslinkers, modifications):
        '''Initializes a new fragments instance'''

        fragments = getfragments(crosslinkers, modifications)
        return cls(getisobaric(crosslinkers, fragments))

    #     PUBLIC

    def todict(self):
        '''Returns a flattened reprsentation with all crosslinker fragments'''

        isobaric = CrosslinkerIsobaric()
        for item in self.values():
            isobaric.update({k: v for k, v in item.items()})
        return isobaric

