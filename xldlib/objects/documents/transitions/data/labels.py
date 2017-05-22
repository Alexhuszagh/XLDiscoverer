'''
    Objects/Documents/Transitions/labels
    ____________________________________

    Definitions for the transition document's labels level.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see "licenses/GNU GPLv3.txt" for more details.
'''

# load modules/submodules
import ast
import itertools as it

import numpy as np

from xldlib.definitions import ZIP
from xldlib.utils import logger, serialization, xictools

from .base import LinearRange, PARENT, repeat, TransitionDataBase
from .crosslink import TransitionsCrosslinkData


# CONSTANTS
# ---------

PRODUCT_COLUMNS = (
    'peptide',
    'score',
    'ev'
)

MS2_COLUMNS = (
    'precursor_z',
    'precursor_rt'
)


# OBJECTS
# -------


@serialization.register('SequencedPopulations')
class SequencedPopulations(dict):
    '''
    Definitions for a sequenced populations holder, which can have
    int or tuple keys.
    '''

    def __getitem__(self, key, default=0, dict_getitem=dict.__getitem__):
        '''Defaultdict like'''

        try:
            return dict_getitem(self, key)
        except KeyError:
            self[key] = default
            return default

    @serialization.tojson
    def __json__(self):
        return dict(self)

    @classmethod
    def loadjson(cls, data, offset=11):
        '''cls.loadjson({"__tuple__: (0,)": 1}) -> {(0,): 1}'''

        return cls({ast.literal_eval(k[offset:]): v for k, v in data.items()})


# LEVEL
# -----


@logger.init('document', 'DEBUG')
class TransitionsLabelsData(TransitionDataBase):
    '''Definitions for the transition labels-level data stores'''

    # KEYS
    # ----
    _child = TransitionsCrosslinkData
    _children = 'crosslink'
    _type = 'labels'

    def __init__(self, *args, **kwds):
        super(TransitionsLabelsData, self).__init__(*args, **kwds)

        if self.get_document().memory:
            self.preload()

    #     PUBLIC

    #    HIERARCHY

    def get_document(self):
        return repeat(PARENT, 2, self)

    def get_file(self):
        return self.parent

    def get_labels(self):
        return self

    def get_crosslink(self, crosslink):
        return self[crosslink]

    def get_charge(self, crosslink, charge):
        return self[crosslink][charge]

    def get_isotope(self, crosslink, charge, isotope):
        return self[crosslink][charge][isotope]

    def iter_crosslink(self):
        return iter(self)

    def iter_charge(self):
        return it.chain.from_iterable(self)

    def iter_isotope(self):
        return repeat(it.chain.from_iterable, 2, self)

    #   PROPERTIES

    # potential pollution from self.attrs... hmm
    #document = property(get_document)
    #file = property(get_file)
    #labels = property(get_labels)

    #   WINDOW

    def get_window_indexes(self):
        return LinearRange(self.window_start, self.window_end)

    def get_window_bounds(self):
        rt = self.get_retentiontime()
        window = self.get_window_indexes()
        return LinearRange(rt[window.start], rt[window.end])

    #    SPECTRA

    def preload(self):
        '''Preloads the spectral arrays to avoid costly I/O operations'''

        self.mem_rt = self.get_retentiontime(force_load=True)
        self.mem_int = {}
        self.mem_mz = {}
        self.mem_int[self.levels] = self.intensity(True)

        for item in it.chain(self.iter_crosslink(), self.iter_charge()):
            self.mem_int[item.levels] = item.intensity(True)

        for isotope in self.iter_isotope():
            self.mem_int[isotope.levels] = isotope.intensity(True)
            self.mem_mz[isotope.levels] = isotope.mz(True)

    def intensity(self, force_load=False):
        '''Returns the spectral intensity for the level'''

        if not force_load and self.get_document().memory:
            return self.mem_int[self.levels]

        else:
            return self.get_file().cache.labels()[:, self.labels_index]

    def child_intensity(self, start=None, end=None, force_load=False):
        '''Returns the spectral intensity for the all children'''

        if not force_load and self.get_document().memory:
            return np.array([self.mem_int[i.levels] for i in self])

        else:
            indexes = tuple(i.crosslink_index for i in self)
            return self.get_file().cache.crosslink()[start:end, indexes].T

    #   METADATA

    def getheaders(self):
        '''Returns all header combinations from a labels group'''

        profile = self.get_document().profile
        mixing = self.get_document().include_mixed_populations

        length = len(self.peptide)
        return profile.getheaders(length, mixing)

    def getusedheaders(self):
        '''Returns the headers used with sequenced and associated counts'''

        profile = self.get_document().profile
        populations = self.sequenced_population

        return {profile.getheader(k): v for k, v in populations.items()}

    def getusedcharges(self):
        return {str(i) for item in self.get_checked_charges() for i in item}

    def get_checked_charges(self):
        return [{i.levels.charge for i in item if i.checked} for item in self]

    def calculate_fit(self):
        for crosslink in self:
            crosslink.calculate_fit()

    #    SETTERS
    #      NEW

    def set_labels(self, data, labeledcrosslink):
        '''Sets the labels-specific data and adds it to the attrs'''

        self.__set_labelattrs(labeledcrosslink)
        self.__set_crosslinkattrs(data, labeledcrosslink)

        indexes = labeledcrosslink.getdataindexes(data)
        for column in PRODUCT_COLUMNS:
            self.setattr(column, list(data.getcolumn(indexes, column)))

        for column in MS2_COLUMNS:
            self.setattr(column, [next(data.getcolumn(indexes, column))])

        self.__set_crosslinks(labeledcrosslink)

    def __set_labelattrs(self, labeledcrosslink):
        '''Sets parameters from the labeled crosslink tuple'''

        self.setattr('file', labeledcrosslink.file)
        self.setattr('frozen', labeledcrosslink.frozen)

        sequenced = SequencedPopulations({labeledcrosslink.sequenced: 0})
        self.setattr('sequenced_population', sequenced)

    def __set_crosslinkattrs(self, data, labeledcrosslink):
        '''Sets parameters from the standard crosslink tuple'''

        standardcrosslink = labeledcrosslink.getcrosslink(data)
        self.setattr('linkname', standardcrosslink.name)
        self.setattr('linktype', standardcrosslink.type)

    def __set_crosslinks(self, labeledcrosslink):
        '''Appends the children crosslinks from the labels definition'''

        precursor_z = self.precursor_z[0]
        for index, label in enumerate(labeledcrosslink.states):
            crosslink = self._child.new(self, str(index))
            crosslink.set_crosslink(label)
            crosslink.set_charges(label, precursor_z)

            self.append(crosslink)

    #    EXTEND

    def add_sequenced(self, crosslink, count=0):
        self.sequenced_population[crosslink.sequenced] += count

    def append_precursors(self, data, labeledcrosslink):
        '''Appends a retentiontime to the current holder'''

        index = labeledcrosslink.getdataindexes(data)[0]

        self.__append_retentiontime(data, index)
        self.__append_charge(data, labeledcrosslink, index)
        self.add_sequenced(labeledcrosslink)

    def __append_retentiontime(self, data, index):
        '''Appends a precursor retention time to the HDF5 attributes'''

        retentiontime = data['matched']['precursor_rt'][index]

        precursor_rt = self.precursor_rt
        precursor_rt.append(retentiontime)
        precursor_rt.sort()

    def __append_charge(self, data, labeledcrosslink, index):
        '''Appends a precursor retention time to the HDF5 attributes'''

        charge = data['matched']['precursor_z'][index]

        precursor_z = self.precursor_z
        if charge not in precursor_z:
            precursor_z.append(charge)
        precursor_z.sort()

        for label, transition in ZIP(labeledcrosslink.states, self):
            transition.set_charges(label, charge)

    #   METADATA

    def set_integrated(self):
        '''Sets the labels spreadsheet with integrated data'''

        spreadsheet = self.spreadsheet
        headers = self.getheaders()
        used = self.getusedcharges()

        self.__set_fitscores(spreadsheet, headers)
        self.__set_amplitudes(spreadsheet, headers, used)

    def __set_fitscores(self, spreadsheet, headers):
        '''Sets the XIC quality of fit scores for each of the transitions'''

        xicscores = [i.get_fitscore() for i in self]
        for header, xicscore in ZIP(headers, xicscores):
            spreadsheet[(header, 'XIC Fit Score')] = xicscore

    def __set_amplitudes(self, spreadsheet, headers, used):
        '''Sets the integrated amplitude data for the transitions'''

        integrated = [i.integrate_data(used) for i in self]
        for header, integraldata in ZIP(headers, integrated):
            for key, attr in integraldata.iterfields():
                spreadsheet[(header, key)] = attr

        for key, attrname in xictools.SPECTRAL_ENUM:
            ratio = xictools.Ratios.fromintegrated(attrname, integrated)
            spreadsheet[(' ', 'Ratio ' + key)] = ratio.tostr()
