'''
    Resources/Chemical_Defs/crosslinkers
    ____________________________________

    Stores crosslinker definitions and links them back to the fragments
    in Resources/Chemical_Defs/modifications.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from namedlist import namedlist

from xldlib.general import sequence
from xldlib.utils import serialization, signals

from . import modifications, dicttools
from .. import paths


__all__ = [
    'CROSSLINKERS',
    'CROSSLINKER_EDITED_SIGNAL',
    'CROSSLINKER_REINDEX_SIGNAL',
    'CROSSLINKER_DELETE_SIGNAL',
    'StoredCrosslinkers',
]


# CONSTANTS
# ---------

CROSSLINKER_FIELDS = [
    "id",
    "name",
    "bridge",
    "fragments",
    "ends",
    ('charge', 0),
    ('active', False),
    ('reporter', ())
]


# PATHS
# -----
CROSSLINKER_PATH = os.path.join(paths.DIRS['data'], 'crosslinkers.json')

# SIGNALS
# -------

CROSSLINKER_EDITED_SIGNAL = signals.Signal()
CROSSLINKER_REINDEX_SIGNAL = signals.Signal()
CROSSLINKER_DELETE_SIGNAL = signals.Signal()


# OBJECTS
# -------


@sequence.serializable("CrosslinkerEnds")
class Ends(namedlist("Ends", "aminoacid terminus deadend")):
    '''Definition for the reactivity of chemical crosslinker ends'''


@sequence.serializable("Crosslinker")
class Crosslinker(namedlist("Crosslinker", CROSSLINKER_FIELDS)):
    '''
    Crosslinker
        id -- Sequential, integer primary keys
        name -- Default crosslinker name
        bridge -- mass of the intact, bridge modification
        fragments -- Modification IDs for the crosslinker fragments
        ends -- Ends instance
        charge -- Integer or sequence of integers for possible charge states of the crosslinker
        active -- crosslinker is currently activated
    '''


@serialization.register('StoredCrosslinkers')
class StoredCrosslinkers(dicttools.StoredNames):
    '''Stores crosslinkers with sequential primary keys'''

    # ERRORS
    # ------
    crosslinker_error = "Crosslinker not recognized"

    def __init__(self, *args, **kwds):
        super(StoredCrosslinkers, self).__init__(*args, **kwds)

        CROSSLINKER_EDITED_SIGNAL.connect(self.modified)

    #    MAGIC

    def __delitem__(self, key, dict_delitem=dict.__delitem__, reindex=True):
        '''sc[key] -> sc[key*] -> value'''

        key = self._keychecker(key, mode=1)
        CROSSLINKER_DELETE_SIGNAL(key)
        super(StoredCrosslinkers, self).__delitem__(key, dict_delitem, reindex)

    #  PROPERTIES

    @property
    def selected(self):
        '''Returns the selected crosslinkers'''

        for id_, crosslinker in self.items():
            if crosslinker.active:
                yield id_, crosslinker

    @property
    def selected_ids(self):
        return tuple(k for k, v in self.selected)

    #    PUBLIC

    def todict(self):
        return {k: v for k, v in self.selected}

    def currentfragments(self, mods=None):
        '''Returns an iterator for all the current fragment modifications'''

        if mods is None:
            mods = modifications.MODIFICATIONS
        for k, v in self.selected:
            for fragment in v.fragments:
                yield fragment, mods[fragment]

    def fragmentstodict(self, mods=None):
        return {v.name: v for k, v in self.currentfragments(mods)}

    def modified(self, crosslinker):
        self.changed[crosslinker.id] = crosslinker

    #      I/O

    def loader(self):
        '''Loads from a target configuration file'''

        document = self._ioload()
        if document is not None:
            keys = sorted(document, key=int)

            for key in keys:
                crosslinker = Crosslinker(*document[key])
                crosslinker.ends = Ends(*crosslinker.ends)
                self[int(key)] = crosslinker

    #    HELPERS

    def _valuechecker(self, crosslinker):
        '''Checks whether a crosslinker object or a possible object'''

        if isinstance(crosslinker, Crosslinker):
            return crosslinker

        elif isinstance(crosslinker, tuple) and len(crosslinker) == 2:
            args, kwds = crosslinker
            assert len(args) == 5, self.crosslinker_error

            return Crosslinker(self._get_new_key(), *args, **kwds)

        elif isinstance(crosslinker, tuple) and len(crosslinker) >= 5:
            return Crosslinker(self._get_new_key(), *crosslinker)

        else:
            raise AssertionError(self.crosslinker_error)


# DATA
# ----

CROSSLINKERS = StoredCrosslinkers(CROSSLINKER_PATH, [
    (1, Crosslinker(id=1,
        name='DSSO',
        bridge='C6 H6 S1 O3',
        fragments=[5941, 5942, 5943, 5944],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=True)),
    (2, Crosslinker(id=2,
        name='Azide Bis',
        bridge='C11 H16 O6 S2',
        fragments=[5945, 5946, 5947],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (3, Crosslinker(id=3,
        name='Azide Bis (UC 1)',
        bridge='C17 H24 S2 O6',
        fragments=[5948, 5949, 5950],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (4, Crosslinker(id=4,
        name='Azide Bis (UC 2)',
        bridge='C16 H23 N3 S2 O6',
        fragments=[5951, 5952, 5953],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (5, Crosslinker(id=5,
        name='Azide Bis (UC 3)',
        bridge='C16 H20 S2 O6',
        fragments=[5954, 5955, 5956],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (6, Crosslinker(id=6,
        name='d0',
        bridge='C8 H10 O3 S1',
        fragments=[5957, 5958, 5959],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (7, Crosslinker(id=7,
        name='d10',
        bridge='C8 2H10 O3 S1',
        fragments=[5960, 5961, 5962],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (8, Crosslinker(id=8,
        name='A 3:6 DSSO',
        bridge='C9 H12 O3 S1',
        fragments=[5963, 5964, 5965],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (9, Crosslinker(id=9,
        name='DHSO',
        bridge='C6 H10 N4 O1 S1',
        fragments=[5966, 5967, 5968],
        ends=Ends(aminoacid=['D,E', 'D,E'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (10, Crosslinker(id=10,
        name='(3,6o)-aDSSO',
        bridge='C8 H10 O4 S1',
        fragments=[5969, 5970, 5971],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (11, Crosslinker(id=11,
        name='TMT-Trioxane',
        bridge='C26 H41 N3 O7',
        fragments=[5972, 5973],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=[0, 1],
        active=False)),
    (12, Crosslinker(id=12,
        name='DSSO (Proteome Discoverer)',
        bridge='C6 H6 S1 O3',
        fragments=[5974, 5975, 5976, 5977, 5978, 5979],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (13, Crosslinker(id=13,
        name='DSSO (Mascot)',
        bridge='C6 H6 S1 O3',
        fragments=[5980, 5981, 5982],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (14, Crosslinker(id=14,
        name='BMSO',
        bridge='C18 H22 N4 S1 O7',
        fragments=[5983, 5984, 5985],
        ends=Ends(aminoacid=['C', 'C'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (15, Crosslinker(id=15,
        name='Bis-Trioxane',
        bridge='C19 H22 O5',
        fragments=[5972, 5973],
        ends=Ends(aminoacid=['K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O']),
        charge=0,
        active=False)),
    (16, Crosslinker(id=16,
        name='Tris-Trioxane',
        bridge='C15 H18 O6',
        fragments=[5972, 5973],
        ends=Ends(aminoacid=['K', 'K', 'K'],
            terminus=modifications.TERMINI['null'],
            deadend=['H2 O', 'H2 O', 'H2 O']),
        charge=0,
        active=False)),
])
