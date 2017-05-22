'''
    XlPy/Spectra/mzxml
    __________________

    Parser for the open, XML data format for raw scan data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import base64
import struct
import xml.sax
import zlib

from collections import namedtuple

import numpy as np

from xldlib.definitions import re, ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger
from xldlib.xlpy.tools import peak_picking


# OBJECTS
# -------
BinaryData = namedtuple("BinaryData", "data precision compression byteorder")


# REGEXP
# ------
MZXML_RT = re.compile(r'^PT((\d*\.?\d*)M)?((\d*\.?\d*)S)?$')


# HELPERS
# -------


@logger.init('scans', level='DEBUG')
class Start(base.BaseObject):
    '''Utilities for processing data from XML start elements'''

    def __init__(self, group):
        super(Start, self).__init__()

        self.source = self.app.discovererthread

        self.group = group
        self._spectrum_type = 'profile'

    def spectrum(self, attrs):
        '''Initializes the scan and sets the scan holder'''

        self.set_newscan(attrs)
        spectrum_type = self.get_spectrum_type(attrs)
        self.scan.setattr('spectrum_type', spectrum_type)

        precursor_num = attrs.get('parentScanNumber')
        if precursor_num is not None:
            self.scan.setattr('precursor_num', int(precursor_num))

        low_mz = attrs.get('lowMz')
        if low_mz is not None:
            self.scan.setattr('low_mz', float(low_mz))

        high_mz = attrs.get('highMz')
        if high_mz is not None:
            self.scan.setattr('high_mz', float(high_mz))

        self.scan.setattrs(
            ms_level=int(attrs['msLevel']),
            polarity=attrs['polarity'],
            basepeak_mz=float(attrs['basePeakMz']),
            basepeak_intensity=float(attrs['basePeakIntensity']),
            total_ion_current=float(attrs['totIonCurrent']),
            peaks_count=int(attrs['peaksCount']))

        retention_time = self.get_retentiontime(attrs['retentionTime'])
        self.scan.setattr('retention_time', retention_time)

    def precursor(self, attrs):
        '''Sets the precursor data for the scan'''

        precursor_num = attrs.get('precursorScanNum')
        if precursor_num is not None:
            self.scan.setattr('precursor_num', int(precursor_num))

        precursor_intensity = attrs.get('precursorIntensity')
        if precursor_intensity is not None:
            self.scan.setattr('precursor_intensity',
                float(precursor_intensity))

        precursor_z = attrs.get('precursorCharge')
        if precursor_z is not None:
            self.scan.setattr('precursor_z', int(precursor_z))
        else:
            self.scan.setattr('precursor_z', 1)

    #     SETTERS

    def set_spectrum_type(self, attrs):
        '''Sets the spectrum type to centroided if centroid acquisition'''

        centroided = attrs.get('centroided', False)
        if centroided and centroided != '0':
            self._spectrum_type = 'centroided'

    def set_newscan(self, attrs):
        '''Sets a new scan group for the startElements'''

        num = int(attrs['num'])
        self.scan = self.group.newscan(num)
        self.scan.setattr('num', num)

    #     GETTERS

    def get_spectrum_type(self, attrs):
        '''Returns the spectrum type {'centroided', 'profile'} for the scan'''

        centroided = attrs.get('centroided')
        if centroided and centroided != '0':
            return 'centroided'
        elif centroided:
            return 'profile'
        else:
            return self._spectrum_type

    def get_retentiontime(self, retention_time):
        '''
        Converts RTs to seconds based on re.match.
        Regex and code used from Martin Strohalm:
        Copyright (C) 2005-2013 Martin Strohalm <www.mmass.org>.
        '''

        match = MZXML_RT.match(retention_time)
        if not match:
            return

        elif match.group(2):
            return float(match.group(2))

        elif match.group(4):
            return float(match.group(4)) / 60


# DATA
# ----

ARRAYS = [
    'mz',
    'intensity'
]


@logger.init('scans', level='DEBUG')
class End(base.BaseObject):
    '''Utilities for processing data from XML end elements'''

    def __init__(self):
        super(End, self).__init__()

        self.source = self.app.discovererthread

        self.set_parameters()

    def scan(self, scan, binarydata):
        '''
        End reading scan and process data. Converts retention time
        to the float format and decodes the peaklists to python lists.
        '''

        if self.get_storespectra(scan):
            arrays = self.get_decoded_scans(scan, binarydata)
            if scan.getattr('spectrum_type') != 'centroided':
                arrays = peak_picking.centroid_scan(*arrays)

            for key, array in ZIP(ARRAYS, arrays):
                scan.create_array(key, array)

    #     SETTERS

    def set_parameters(self):
        '''Sets the default parameters for spectral searching'''

        self.checkprecursor = defaults.DEFAULTS['check_precursor']
        self.ms1level = defaults.DEFAULTS['ms1_scan_level']
        self.precursorlevel = defaults.DEFAULTS['precursor_scan_level']
        self.productlevel = defaults.DEFAULTS['product_scan_level']
        self.scanlevels = {self.precursorlevel, self.productlevel}

        # sets whether peptide mass fingerprinting is active
        self.fingerprinting = self.source.fingerprinting
        self.reporterions = self.source.reporterions

    #     GETTERS

    def get_storespectra(self, group):
        '''
        Determines whether to store the spectral data. Since the scan
        hierarchy is well-defined, only store if storing unmatched data
        or if storing quantitative data.
        '''

        level = group.getattr('ms_level')
        if level == self.precursorlevel and self.checkprecursor:
            return True
        elif level == self.productlevel and self.reporterions:
            return True
        elif level in self.scanlevels and self.fingerprinting:
            return True
        elif level == self.ms1level and self.source.quantitative:
            return True
        return False

    def get_decoded_scans(self, group, binarydata):
        '''Unpacks m/z-int base64 encoded data to lists.'''

        data = self.get_decoded_b64(binarydata)
        if not data:
            return np.array([]), np.array([])

        prec = ['f', 'd'][binarydata.precision == 64]
        byte = defaults.DEFAULTS['byte_order'][binarydata.byteorder]
        count = len(data) // struct.calcsize(byte + prec)
        values = struct.unpack(byte + prec*count, data)

        return values[::2], values[1::2]

    @staticmethod
    def get_decoded_b64(binarydata):
        '''Decodes the for a given scan and returns the peak lists'''

        if binarydata.precision == 64:
            data = base64.b64decode(binarydata.data)
        else:
            data = base64.b32decode(binarydata.data)

        if binarydata.compression == 'zlib':
            try:
                return zlib.decompress(data)
            except zlib.error:
                return ''


# HANDLER
# -------


@logger.init('scans', level='DEBUG')
class RunHandler(xml.sax.handler.ContentHandler):
    '''
    Custom handler for scan data and metadata, while ignoring run or
    filetype parameters.
    '''

    def __init__(self, group):
        xml.sax.ContentHandler.__init__(self)

        self.group = group

        self.start = Start(self.group)
        self.end = End()

        self.set_defaults()

    #    XML ELEMENTS

    def startElement(self, name, attrs):
        '''Element started.'''

        if name == 'dataProcessing':
            self.start.set_spectrum_type(attrs)

        elif name == 'scan':
            self.start.spectrum(attrs)
            self.scan = self.start.scan

        elif name == 'peaks':
            self.peaks = True
            self._peaks = []
            self._byteorder = attrs['byteOrder']
            self._compression = attrs['compressionType']
            self._precision = int(attrs['precision'])

        elif name == 'precursorMz':
            self.precursor = True
            self._precursor = []
            self.start.precursor(attrs)

    def endElement(self, name):
        '''Element ended.'''

        if name == 'scan':
            self.end.scan(self.scan, self.binarydata)
            self.binarydata = None

        elif name == 'peaks':
            self.peaks = False
            self.binarydata = BinaryData(''.join(self._peaks),
                self._precision, self._compression, self._byteorder)
            self._peaks = None

        elif name == 'precursorMz':
            self.precursor = False
            if self._precursor:
                precursor_mz = float(''.join(self._precursor))
                self.start.scan.setattr('precursor_mz', precursor_mz)

            self._precursor = None

    def characters(self, text):
        '''Grab characters.'''

        if self.precursor:
            self._precursor.append(text)

        elif self.peaks:
            self._peaks.append(text)

    #     SETTERS

    def set_defaults(self):
        '''Sets the default values for scan grouping in the sax parser'''

        self.scan = None
        self.peaks = False
        self.precursor = False
        self._byteorder = None
        self._compression = None
        self._precision = None
        self.binarydata = None



# PARSER
# ------


@logger.init('scans', level='DEBUG')
class ParseXml(base.BaseObject):
    '''
    Processes the XML-like open source data-format, common
    with the TransProteomic Pipeline.
    '''

    @decorators.overloaded
    def __init__(self, fileobj, group):
        super(ParseXml, self).__init__()

        self.fileobj = fileobj
        self.group = group
        self.source = self.app.discovererthread

    @logger.raise_error
    def __call__(self):
        '''On start'''

        handler = RunHandler(self.group)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(self.fileobj)

        self.fileobj.close()
