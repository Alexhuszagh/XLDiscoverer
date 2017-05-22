'''
    XlPy/Spectra/pava
    _________________

    Parser for the MGF-like FTMSFullMs PAVA format, which contains
    raw spectral data from the MS1 level.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules
import sys

from collections import OrderedDict

import numpy as np

from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.xlpy.ms1quantitation.extraction import scans
from xldlib.xlpy.tools import peak_picking

from . import scan_parser


# PARSERS
# -------

PARSERS = {
    'None.None.None, Pava FullMs': 'processfullms'
}

FULLMS = OrderedDict([
    ('num', [(1, int)]),
    ('retention_time', [(2, float)]),
    ('total_injection_time', [(3, float)]),
    ('total_ion_current', [(4, float)]),
    ('basepeak_mz', [(5, float)]),
    ('basepeak_intensity', [(6, float)])
])


# OBJECTS
# -------


@logger.init('scans', level='DEBUG')
class ParseFullms(base.BaseObject):
    '''
    Parses MGF file format using series of known subs (specific
    to each version of MGF file) and stores data in dictionary.
    MGF Format:
        Scan#: 1
        Ret.Time: 0.00326333333333333
        IonInjectionTime(ms): 500
        TotalIonCurrent: 619888.9375
        BasePeakMass: 371.101409912109
        BasePeakIntensity: 112842.8515625
        350.00031   .000
        ...
        Scan#: 2
    '''

    # CENTROIDING
    # -----------
    _centroided = None

    def __init__(self, row, group, fileobj):
        super(ParseFullms, self).__init__()

        self.row = row
        self.group = group
        self.fileobj = fileobj

        engine = row.engines['ms1']
        self.extractor = scans.ChromatogramExtractor(row)
        self.scan_finder = scan_parser.ScanFinder.fromengine(engine, end=True)

        self._parser = getattr(self, PARSERS[engine.tostr()])
        self.re_scan = re.compile(engine.defaults.regexp)

    @logger.raise_error
    def __call__(self):
        '''
        On start. Reads chunks until done for faster speeds than
        readline.
        '''

        chunk = True
        while chunk:
            chunk = self.fileobj.read(defaults.DEFAULTS['chunk_size'])
            for scan in self.scan_finder(chunk):
                self._parser(scan)

        self.extractor.spectratotables()
        self.extractor.set_windows()
        self.fileobj.close()
        del self.extractor

    #    PROCESSORS

    def processfullms(self, scan):
        '''
        Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self._add_spectra(). Processes PAVA-like formats.
        '''

        match = self.re_scan.split(scan)
        scandata = self.getscandata(match, FULLMS)
        group = self.group.newscan(**scandata)

        mzs, intensity = self.getspectra(match[7])
        self.extractor(scandata['retention_time'], mzs, intensity)

    def processspectra(self, spectra):
        '''Processes the scan spectral data.'''

        array = np.fromstring(spectra, sep='\t', dtype=float)
        if len(array) == 1:
            # no values
            return np.array([]), np.array([])

        return array[::2], array[1::2]

    #     GETTERS

    def getscandata(self, match, fields):
        '''
        Processes the re-matched data using fields denoting the position
        and type-cast for the data.
        '''

        scandata = {}
        for key, values in fields.items():
            for position, typecast, in values:
                value = match[position]
                # skip null strings
                if value:
                    scandata[key] = typecast(value)

        return scandata

    def getspectra(self, spectra):
        '''
        Extracts the spectral data from the scan header and converts
        profile data to centroided data.
        '''

        mzs, intensity = self.processspectra(spectra)
        return self._getcentroided(mzs, intensity)

    def _getcentroided(self, mzs, intensity):
        '''Returns the centroided peaklists from the MS1 data'''

        if self._centroided is None:
            try:
                return self._detectcentroided(mzs, intensity)
            except AssertionError:
                print("Unable to detect if peaks are centroided or "
                    "profile, returning profile data", file=sys.stderr)
                return mzs, intensity

        elif self._centroided is False:
            return peak_picking.centroid_scan(mzs, intensity)
        else:
            return mzs, intensity

    #     HELPERS

    def _detectcentroided(self, mzs, intensity):
        '''
        Detects whether the file has centroided or profile-type
        peaks.
        :
            scan -- dict holder for scan data
        '''

        self._centroided = peak_picking.check_centroided(intensity)
        if self._centroided is False:
            return peak_picking.centroid_scan(mzs, intensity)
        else:
            return mzs, intensity
