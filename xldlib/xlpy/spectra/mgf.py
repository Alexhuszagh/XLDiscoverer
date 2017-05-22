'''
    XlPy/Spectra/mgf
    ________________

    Parser for the highly variable MGF-like file formats, which
    have a scan delimiter (BEGIN IONS), header, spectral data, and
    an end scan delimiter (END IONS).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function, division

# load modules
import sys

from collections import OrderedDict

import numpy as np

from xldlib import exception
from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import scan_parser


# CONSTANTS
# ---------

DELIMITERS = (' ', '\t')


# PARSERS
# -------

PARSERS = {
    'None.None.None, PAVA': 'processpava',
    #'zth': 'processzth',
    'None.None.None, MS Convert': 'processmsconvert',
    'None.None.None, ProteoWizard': 'processproteowizard',
}

PAVA = OrderedDict([
    ('num', [(3, int)]),
    ('retention_time', [(4, float)]),
    ('file', [(5, str)]),
    ('precursor_num', [(2, int)]),
    ('precursor_mz', [(6, float)]),
    ('precursor_intensity', [(7, float), (8, float)]),
    ('precursor_z', [(10, int)])
])

ZTH = OrderedDict([
    ('num', [(4, int)]),
    ('retention_time', [(9, float)]),
    ('file', [(2, str)]),
    ('precursor_mz', [(5, float)]),
    ('precursor_intensity', [(6, float)]),
    ('precursor_z', [(8, int)]),
])

MS_CONVERT = OrderedDict([
    ('num', [(3, int)]),
    ('retention_time', [(4, float)]),
    ('file', [(1, str)]),
    ('precursor_mz', [(5, float)]),
    ('precursor_intensity', [(6, float)]),
    ('precursor_z', [(8, int)])
])

PROTEO_WIZARD = OrderedDict([
    ('num', [(3, int)]),
    ('retention_time', [(7, float)]),
    ('file', [(1, str)]),
    ('precursor_mz', [(4, float)]),
    ('precursor_intensity', [(5, float)]),
    ('precursor_z', [(6, int)]),
])

ARRAYS = {
    2: {
        'mz': [0, float],
        'intensity': [1, float]
    },
    3: {
        'mz': [0, float],
        'z': [1, int],
        'intensity': [2, float]
    }
}

# OBJECTS
# -------


@logger.init('scans', level='DEBUG')
class ParseText(base.BaseObject):
    '''
    Parses MGF file format using series of known subs (specific
    to each version of MGF file) and stores data in dictionary.
    MGF Format:
        BEGIN IONS
        scan=470
        PEPMASS=473.456
        ...
        475.34\t1800
        ...
        END IONS
    '''

    def __init__(self, fileobj, group, engine):
        super(ParseText, self).__init__()

        self.fileobj = fileobj
        self.group = group
        self.source = self.app.discovererthread
        self.scan_finder = scan_parser.ScanFinder.fromengine(engine)

        self._parser = getattr(self, PARSERS[engine.tostr()])
        self.re_scan = re.compile(engine.defaults.regexp)

    @logger.raise_error
    def __call__(self):
        '''
        On start. Reads chunks until file end, using large chunk
        sizes for rapid, high-throughput performance.
        '''

        chunk = True
        while chunk:
            chunk = self.fileobj.read(defaults.DEFAULTS['chunk_size'])
            for scan in self.scan_finder(chunk):
                self._parser(scan)

        self.fileobj.close()

    #    PROCESSORS

    def processpava(self, scan):
        '''
        Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self.processdata(). Processes PAVA-like formats.
        '''

        match = self.re_scan.split(scan)
        scandata = self.getscandata(match, PAVA)
        group = self.group.newscan(**scandata)

        # process data
        if self.getstorespectra(group):
            self.processdata(group, match[11])

#    def processzth(self, scan):
#        '''
#        Processes a single scan and stores the data in self.data.
#        Stores the meta-data directly and then processes the scan
#        spectra via self.processdata(). Processes ZTH-like formats.
#        '''
#
#
#        match = self.re_scan.split(scan)
#        scandata = self.getscandata(match, ZTH)
#        scandata['retention_time'] /= 60
#        group = self.get_group(scandata)
#
#        # process data
#        if self.getstorespectra(group):
#            self.processdata(group, match[11])

    def processmsconvert(self, scan):
        '''
        Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self.processdata(). Processes TPP-like formats.
        '''

        match = self.re_scan.split(scan)
        scandata = self.getscandata(match, MS_CONVERT)
        scandata['retention_time'] /= 60
        group = self.group.newscan(**scandata)

        # process data
        if self.getstorespectra(group):
            self.processdata(group, match[9])

    def processproteowizard(self, scan):
        '''
        Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self.processdata(). Processes TPP-like formats.
        '''

        match = self.re_scan.split(scan)
        scandata = self.getscandata(match, PROTEO_WIZARD)
        scandata['retention_time'] /= 60
        group = self.group.newscan(**scandata)

        # process data
        if self.getstorespectra(group):
            self.processdata(group, match[9])

    def processdata(self, group, spectra):
        '''Processes the scan spectral data.'''

        # process to list and then parse
        delimiter = self.getdelimiter(spectra)
        array = np.fromstring(spectra, sep=delimiter, dtype=float)
        if array.size == 1:
            return

        columns = self.getspectralcolumns(spectra, delimiter)
        arrays = ARRAYS.get(columns)
        if arrays is None:
            print(exception.CODES['018'], file=sys.stderr)
            return

        for key, (index, dtype) in arrays.items():
            newarr = array[index:-1:columns].astype(dtype)
            group.newarray(key, newarr)

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

        # charge not listed in scan header if charge == 1
        scandata.setdefault('precursor_z', 1)
        return scandata

    def getstorespectra(self, group):
        '''Determines whether to store the spectral data'''

        if not hasattr(self, "storespectra"):
            self.setstorespectra(group)

        return self.storespectra

    def getdelimiter(self, spectra):
        '''Returns the default spectra separator if not already set'''

        if not hasattr(self, "_delimiter"):
            self.setdelimiter(spectra)
        return self._delimiter

    def getspectralcolumns(self, spectra, delimiter):
        '''
        Returns number of spectral columns for each specrral data entry
            Ex. 1:
                475.34\t1800
            Ex. 2:
                475.34\t1\t1800
        '''

        if not hasattr(self, "_spectralcolumns"):
            self.setspectralcolumns(spectra, delimiter)
        return self._spectralcolumns

    #     SETTERS

    def setdelimiter(self, spectra):
        '''Sets the spectral delimiter for the MS scans'''

        line = spectra.splitlines()[0]
        for delimiter in DELIMITERS:
            if delimiter in line:
                self._delimiter = delimiter
                break

    def setstorespectra(self, group):
        '''
        Sets whether or not to store spectral data. The spectral data
        is only stored if the MS3 precursor is not listed in the scan
        header and the check precursor flag is on, or mass fingerprinting
        is active.
        '''

        verify = (defaults.DEFAULTS['check_precursor'] and
            self.group.isprecursor() and
            not group.hasattr('precursor_num'))

        reporterion = (self.source.reporterions and
            self.group.isproduct())

        self.storespectra = any((
            verify,
            self.source.fingerprinting,
            reporterion
        ))

    def setspectralcolumns(self, spectra, delimiter):
        '''Sets the number of columns in the spectral data'''

        self._spectralcolumns = len(spectra.splitlines()[0].split(delimiter))
