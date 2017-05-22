'''
    XlPy/MS1Quantitation/Extraction/Scans
    _____________________________________

    Extracts ion chromatograms from MS1 scans.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import weakref

from collections import defaultdict, namedtuple

import numpy as np

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# OBJECTS
# -------

Scan = namedtuple("Scan", "rows mzs intensity")


class DimensionTemplate(list):
    '''List with a defined dimension for a single side'''

    def __init__(self, dimensions, template=None):
        super(DimensionTemplate, self).__init__()

        self.dimensions = dimensions
        if template is None:
            template = [0.] * self.dimensions
        self.template = template

    def newrow(self):
        self.append(self.template[:])


# DATA
# ----
# full range of mass spectra
BINS = np.arange(50, 2000, 50)

EXTENDABLES = (
    'mz',
    'intensity',
    'charge',
    'crosslink',
    'labels'
)


# HELPERS
# -------


def groupspectra(scan):
    '''
    Groups scans within a certain m/z window that were found deconvoluted
    from the self.mzs array previously.
    '''

    mzs = defaultdict(list)
    intensities = defaultdict(list)

    for row, mz, intensity in ZIP(*scan):
        mzs[row].append(mz)
        intensities[row].append(intensity)

    return mzs, intensities


def digitizebins(array, positions, reshape=False):
    '''Digitizes the array based on a series of bins'''

    array = np.array(array)

    out = {}
    # digitizer is 1 indexed, apparently...
    for index in range(BINS.size+1):
        value = array[positions == index]
        if reshape:
            value = value.reshape((-1, 1))
        out[index] = value

    return out


def digitizelist(lst, positions):
    '''Digitizes the given list to a defaultdict'''

    out = defaultdict(list)
    for index, position in enumerate(positions):
        out[position].append(lst[index])

    return out


# EXTRACTION
# ----------


@logger.init('quantitative', 'DEBUG')
class ChromatogramExtractor(base.BaseObject):
    '''Extracts ion chromatograms from a given MS1 scan's spectral data.'''

    def __init__(self, row):
        super(ChromatogramExtractor, self).__init__()

        self.row = row
        self.source = weakref.proxy(self.app.discovererthread)

        self.setparameters()
        self.setisotopes()
        self.setcharges()
        self.setcrosslinks()
        self.setlabels()
        self.file = []

        self.counter = 0

    def __call__(self, retentiontime, mzs, intensity):
        '''Processes the spectral data and appends the retentiontime'''

        self.retentiontime.append(retentiontime)
        for name in EXTENDABLES:
            getattr(self, name).newrow()

        scans = self.getmzwindow(mzs, intensity)
        for index, scan in scans:
            groupedmzs, groupedintensities = groupspectra(scan)
            self.setscandata(index, groupedmzs, groupedintensities)

        self.setchargedata()
        self.setcrosslinkdata()
        self.setlabeldata()
        self.file.append(sum(self.labels[-1]))

        # dump memory data to PyTables
        self.counter += 1
        if not (self.counter % self.source.transitions.iorows):
            self.spectratotables()

    #    SETTERS

    def setisotopes(self):
        '''Creates a compact array for vectorized functions from the mzs'''

        self.mzs = self.row.transitions.getattr('massorder')
        positions = np.digitize(self.mzs, BINS)
        self.binned_mzs = digitizebins(self.mzs, positions, reshape=True)
        self.indexes = digitizelist(range(len(self.mzs)), positions)

        dimensions = len(self.mzs)
        self.mz = DimensionTemplate(dimensions, template=self.mzs)
        self.intensity = DimensionTemplate(dimensions)
        self.retentiontime = []

    def setcharges(self):
        '''Sets the charge lookups for quick processing'''

        self.chargeindexes = []
        for charge in self.row.transitions.iter_charge():
            indexes = [i.getattr('isotope_index') for i in charge]
            self.chargeindexes.append(indexes)

        self.charge = DimensionTemplate(len(self.chargeindexes))

    def setcrosslinks(self):
        '''Sets the crosslink lookups for quick processing'''

        self.crosslinkindexes = []
        for crosslink in self.row.transitions.iter_crosslink():
            indexes = [i.getattr('charge_index') for i in crosslink]
            self.crosslinkindexes.append(indexes)

        self.crosslink = DimensionTemplate(len(self.crosslinkindexes))

    def setlabels(self):
        '''Sets the labels lookups for quick processing'''

        self.labelindexes = []
        for labels in self.row.transitions.iter_labels():
            indexes = [i.getattr('crosslink_index') for i in labels]
            self.labelindexes.append(indexes)

        self.labels = DimensionTemplate(len(self.labelindexes))

    def setparameters(self):
        '''Binds the default parameters to the class for quick lookups'''

        self.ppm_threshold = defaults.DEFAULTS['ppm_threshold'] * 1e-6
        self.minus = defaults.DEFAULTS['minus_time_window']
        self.plus = defaults.DEFAULTS['minus_time_window']

    def setscandata(self, binned_index, groupedmzs, groupedintensities):
        '''Adds in all the scan data from the grouped scans'''

        # grab our binned indexes
        indexes = self.indexes[binned_index]

        # add all the matched data
        for index, mz in groupedmzs.items():
            value_index = indexes[index]
            intensity = groupedintensities[index]

            self.mz[-1][value_index] = np.average(mz, weights=intensity)
            self.intensity[-1][value_index] = np.sum(intensity)

    def setchargedata(self):
        '''Updates the charge data for the holder'''

        for index, isotopes in enumerate(self.chargeindexes):
            value = sum(self.intensity[-1][i] for i in isotopes)
            self.charge[-1][index] = value

    def setcrosslinkdata(self):
        '''Updates the charge data for the holder'''

        for index, charges in enumerate(self.crosslinkindexes):
            value = sum(self.charge[-1][i] for i in charges)
            self.crosslink[-1][index] = value

    def setlabeldata(self):
        '''Updates the charge data for the holder'''

        for index, crosslinks in enumerate(self.labelindexes):
            value = sum(self.crosslink[-1][i] for i in crosslinks)
            self.labels[-1][index] = value

    def set_windows(self):
        '''Sets the start and the end windows for group'''

        rt = np.array(getattr(self.row.transitions.cache, 'retentiontime')())
        for labels in self.row.transitions.iter_labels():
            rts = labels.getattr('precursor_rt')
            start = min(rts) - self.minus
            end = max(rts) + self.plus

            indexes, = np.where((start < rt) & (end > rt))
            labels.setattr('window_start', indexes[0] - 1)
            labels.setattr('window_end', indexes[-1] + 1)

    #    GETTERS

    def getmzwindow(self, mzs, intensity):
        '''
        Filters the scan mz values based on the min and max of the
        transition window, to filter for only those in the crosslinker
        window.
        '''

        # use binning to allow scan extraction in roughly O(n) time,
        # where n is the size of the mzs, and m is the size of the query
        # otherwise, scales as O(n*m) time
        positions = np.digitize(mzs, BINS)
        binned_mzs = digitizebins(mzs, positions)
        binned_intensity = digitizebins(intensity, positions)

        # np.digitize 1-indexes everything, so has to be BINS.size+1
        for index in range(BINS.size+1):
            diff = abs(binned_mzs[index] - self.binned_mzs[index])
            ppm = diff / self.binned_mzs[index]
            rows, cols = np.where(ppm <= self.ppm_threshold)

            mzs = binned_mzs[index][cols]
            intensity = binned_intensity[index][cols]
            yield index, Scan(rows, mzs, intensity)

    #    HELPERS

    @logger.call('quantitative', 'debug')
    def spectratotables(self):
        '''
        Ends the scan windows and then converts the mz/intensity peaklists
        to PyTables arrays.
        '''

        for name in ('retentiontime', 'file') + EXTENDABLES:
            lst = getattr(self, name)
            arr = getattr(self.row.transitions.cache, name)()
            arr.append(lst)
            # free up memory for future
            del lst[:]
