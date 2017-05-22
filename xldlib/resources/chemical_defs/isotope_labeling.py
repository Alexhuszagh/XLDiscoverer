'''
    Resources/Chemical_Defs/isotope_labeling
    ________________________________________

    Chemical building-block definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it
import os

from collections import defaultdict, Mapping

from namedlist import namedlist

import six

from xldlib.chemical.building_blocks import DEUTERIUM
from xldlib.definitions import Json
from xldlib.general import mapping, sequence
from xldlib.resources import paths
from xldlib.utils import serialization, signals

from . import dicttools, modifications
from .crosslinkers import CROSSLINKERS
from ..parameters import defaults


__all__ = [
    'Profile',
    'PROFILES',
    'PROFILE_EDITED_SIGNAL',
    'PROFILE_REINDEX_SIGNAL',
    'PROFILE_DELETE_SIGNAL'
]

# PATHS
# -----
PROFILES_PATH = os.path.join(paths.DIRS['data'], 'isotope_labels.json')


# CONSTANTS
# ---------

POPULATION_FIELDS = [
    "header",
    "crosslinker",
    ("delta_retentiontime", 0),
    ("modifications", ())
]

# SIGNALS
# -------

PROFILE_EDITED_SIGNAL = signals.Signal()
PROFILE_REINDEX_SIGNAL = signals.Signal()
PROFILE_DELETE_SIGNAL = signals.Signal()


# OBJECTS
# -------


@sequence.serializable('IsotopeLabeledPopulation')
class Population(namedlist("Population", POPULATION_FIELDS)):
    '''
    Defines an isotope-labeling population state
        Population(header="Light DSSO", crosslinker=0, modifications=[])
    '''

    @classmethod
    def blank(cls, crosslinker_id):
        '''Initiates a blank population from a crosslinker ID'''

        crosslinker = CROSSLINKERS[crosslinker_id]
        return cls(crosslinker.name, crosslinker_id)

    #     PUBLIC

    def clear(self):
        del self.modifications[:]

    def removenulls(self):
        '''Remove all null values from the current modifications'''

        for index in range(len(self.modifications)-1, -1, -1):
            if self.modifications[index] is None:
                del self.modifications[index]

    def getmodifications(self):
        for uniprotid in self.modifications:
            yield modifications.MODIFICATIONS[uniprotid]

    def getcrosslinker(self):
        return CROSSLINKERS[self.crosslinker]

    def islocked(self, formula_parser):
        '''Checks if the population is locked'''

        mods = (modifications.MODIFICATIONS[i] for i in self.modifications)
        formulas = (formula_parser(i.formula) for i in mods)

        crosslinker = CROSSLINKERS[self.crosslinker]
        bridge = formula_parser(crosslinker.bridge)

        return all((
            self.delta_retentiontime == 0,
            not any(DEUTERIUM in i.get('H', {}) for i in formulas),
            DEUTERIUM not in bridge.get('H', {})
        ))


@sequence.serializable('IsotopeLabeledProfile')
class Profile(namedlist("Profile", "id name engine version populations")):
    '''Subclass with a memoizer'''

    def __init__(self, *args, **kwds):
        super(Profile, self).__init__(*args, **kwds)

        self._names = {i.header for i in self.populations}

    #    PROPERTIES

    @property
    def len(self):
        return len(self.populations)

    @property
    def crosslinker_ids(self):
        return [i.crosslinker for i in self.populations]

    @property
    def crosslinkers(self):
        return [CROSSLINKERS[i].name for i in self.crosslinker_ids]

    @property
    def row_count(self):
        return max(len(i.modifications) for i in self.populations)

    @property
    def column_count(self):
        return len(self.populations)

    @property
    def headers(self):
        return [i.header for i in self.populations]

    #     GETTERS

    def getunique(self, name):
        '''Returns the unique version of the name'''

        if name in self._names:
            counter = 1
            while '{0} {1}'.format(name, counter) in self._names:
                counter += 1
            return '{0} {1}'.format(name, counter)
        return name

    def getlabels(self):
        return {i: set(j.getmodifications()) for i, j in
                   enumerate(self.populations)}

    def getheader(self, state):
        populations = (self.populations[i] for i in state)
        return ' - '.join(i.header for i in populations)

    def getheaders(self, lengths, mixing):
        '''Returns all possible headers from the profile'''

        if isinstance(lengths, six.integer_types):
            lengths = {lengths}

        number = len(self.populations)
        if mixing:
            states = [it.product(range(number), repeat=i) for i in lengths]
            states = sorted(i for item in states for i in item)
        else:
            states = []
            for value in range(number):
                states.extend((tuple(it.repeat(value, n)) for n in lengths))

        return [self.getheader(i) for i in states]

    #     PUBLIC

    @classmethod
    def fromlist(cls, profile, populations_index=-1):
        '''Instantiates a current instance from a list instance'''

        populations = profile.pop(populations_index)
        populations = [Population(*i) for i in populations]
        profile.append(populations)

        return cls(*profile)

    @classmethod
    def blank(cls, name, crosslinker_ids, id_=None,
        engine="Protein Prospector", version="5.13.1, TEXT"):
        '''Instantiates a new, blank instance'''

        if id_ is None:
            id_ = max(PROFILES) + 1
        populations = [Population.blank(i) for i in crosslinker_ids]

        return cls(
            id_,
            name,
            engine,
            version,
            populations)

    def rename(self, index, newname):
        '''Renames a population'''

        population = self.populations[index]
        oldname = population.header

        if newname != oldname:
            newname = self.getunique(newname)

            # update memoizer
            self._names.remove(oldname)
            self._names.add(newname)

            self.populations[index] = population._replace(header=newname)

    def append(self):
        '''Appends a new, blank population to the current holder'''

        name = self.getunique('Population')
        population = self.populations[-1]._replace(header=name,
            modifications=[])
        self.populations.append(population)
        self._names.add(name)

    def clear(self):
        '''Clears the current populations'''

        for population in self.populations:
            population.clear()

    def resize(self, count):
        '''Resizes the populations due to experiment count changes'''

        current = len(self.populations)
        if count > current:
            for index in range(current, count):
                self.append()

        elif count < current:
            for index in range(current -1, count - 1, -1):
                population = self.populations.pop(index)
                self._names.remove(population.header)

    def removenulls(self):
        for population in self.populations:
            population.removenulls()

    def islocked(self, formula_parser):
        '''Checks if there is a retentiontime lock for the profile'''

        return all((
            defaults.DEFAULTS['retentiontime_lock'],
            all(i.islocked(formula_parser) for i in self.populations)
        ))


@serialization.register('StoredIsotopeProfiles')
class StoredIsotopeProfiles(dicttools.SequentialStorage):
    '''Stores isotope profiles with sequential primary keys'''

    profile_error = "Crosslinker profile not recognized"

    __update = dict.update

    def __init__(self, path, defaults):
        super(StoredIsotopeProfiles, self).__init__(path, defaults)

        self.crosslinkers = defaultdict(set)
        self.__setcrosslinkers(defaults)

        self.engines = defaultdict(set)
        self.__setengines(defaults)

        self.loader()

        PROFILE_EDITED_SIGNAL.connect(self.modified)

    #     MAGIC

    def __contains__(self, key, dict_contains=dict.__contains__):
        '''key in si -> True'''

        if isinstance(key, six.integer_types):
            return dict_contains(self, key)

        elif isinstance(key, tuple):
            return key in self.crosslinkers or key in self.engines

        else:
            return False

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''si[key] -> si[key*] -> value'''

        if isinstance(key, six.integer_types):
            return dict_getitem(self, key)

        elif isinstance(key, tuple) and key in self.crosslinkers:
            return self.crosslinkers[key]

        elif isinstance(key, tuple) and key in self.engines:
            return self.engines[key]

        else:
            raise KeyError(key)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''si[key] = value -> si[key*] = value'''

        value = self._valuechecker(value)
        key = self._keychecker(key)

        crosslinkers = self.getcrosslinker(value)
        self.crosslinkers[crosslinkers].add(value.id)

        engine = self.get_engine(value)
        self.engines[engine].add(value.id)

        self.changed[key] = value
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__, reindex=True):
        '''si[key] -> si[key*] -> value'''

        key = self._keychecker(key, mode=1)

        value = self[key]
        crosslinkers = self.getcrosslinker(value)
        self.crosslinkers[crosslinkers].remove(value.id)
        if not self.crosslinkers[crosslinkers]:
            del self.crosslinkers[crosslinkers]

        engine = self.get_engine(value)
        self.engines[engine].remove(value.id)
        if not self.engines[engine]:
            del self.engines[engine]

        dict_delitem(self, key)
        if reindex:
            self.reindex()

        PROFILE_DELETE_SIGNAL(key)

    #   PROPERTIES

    @property
    def current_id(self):
        return defaults.DEFAULTS['current_isotope_profile']

    @current_id.setter
    def current_id(self, value):
        defaults.DEFAULTS['current_isotope_profile'] = value

    @property
    def current(self):
        return self[self.current_id]

    @property
    def selected_ids(self):
        return self[CROSSLINKERS.selected_ids]

    @property
    def selected_profiles(self):
        return {i: self[i] for i in self.selected_ids}

     #    SETTERS

    def __setcrosslinkers(self, defaults):
        '''Sets the modification names from the defaults'''

        if isinstance(defaults, Mapping):
            for value in defaults.values():
                crosslinkers = self.getcrosslinker(value)
                self.crosslinkers[crosslinkers].add(value.id)

        elif isinstance(defaults, list):
            for key, value in defaults:
                crosslinkers = self.getcrosslinker(value)
                self.crosslinkers[crosslinkers].add(value.id)

    def __setengines(self, defaults):
        '''Sets the modification names from the defaults'''

        if isinstance(defaults, Mapping):
            for value in defaults.values():
                engine = self.get_engine(value)
                self.engines[engine].add(value.id)

        elif isinstance(defaults, list):
            for key, value in defaults:
                engine = self.get_engine(value)
                self.engines[engine].add(value.id)

    def modified(self, profile):
        self.changed[profile.id] = profile

    #    GETTERS

    @staticmethod
    def getcrosslinker(profile):
        '''Returns the sorted crosslinker keys from the profile'''

        return tuple(sorted(set(i.crosslinker for i in profile.populations)))

    @staticmethod
    def get_engine(profile):
        '''Returns the sorted crosslinker keys from the profile'''

        return (profile.engine, profile.version)

    #     HELPERS

    def _valuechecker(self, profile):
        '''Checks whether a profile object or a possible object'''

        if isinstance(profile, Profile):
            return profile

        elif isinstance(profile, tuple) and len(profile) == 2:
            return Profile(self._get_new_key(), *profile)

        else:
            raise AssertionError(self.profile_error)

    #      I/O

    def save(self):
        '''Dumps the JSON configurations to file'''

        with open(self.path, "w") as dump:
            Json.dump(self.changed, dump, sort_keys=True, indent=4,
                default=mapping.tojson)

    def loader(self):
        '''Loads from a target configuration file'''

        document = self._ioload()
        if document is not None:
            keys = sorted(document, key=int)

            for key in keys:
                profile = Profile.fromlist(document[key])
                self[int(key)] = profile


# DATA
# ----

PROFILES = StoredIsotopeProfiles(PROFILES_PATH, [
    (1, Profile(id=1,
        name="Label-Free DSSO",
        engine="Protein Prospector",
        version="5.13.1, TEXT",
        populations=[
            Population(header="DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[])
        ])),
    (2, Profile(id=2,
        name="SILAC 13C6 15N2-K",
        engine="Protein Prospector",
        version="5.13.1, TEXT",
        populations=[
            Population(header="Light DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[]),
            Population(header="SILAC 13C6 15N2 DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[
                    126
                ])
        ])),
    (3, Profile(id=3,
        name="15N Backbone Labeling",
        engine="Protein Prospector",
        version="5.13.1, TEXT",
        populations=[
            Population(header="Light DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[]),
            Population(header="15N-Labelled DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[
                    131,
                    132,
                    133,
                    134,
                    135,
                    136,
                    137,
                    138,
                    139,
                    140,
                    141,
                    142,
                    143,
                    144,
                    151,
                    152,
                    153,
                    154,
                    155,
                    156
                ])
        ])),
    (4, Profile(id=4,
        name="SILAC 13C6 15N2-K 15N4-R",
        engine="Protein Prospector",
        version="5.13.1, TEXT",
        populations=[
            Population(header="Light DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[]),
            Population(header="SILAC 13C6 15N2 15N4 DSSO",
                crosslinker=1,
                delta_retentiontime=0,
                modifications=[
                    126,
                    128
                ])
        ]))
])
