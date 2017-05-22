'''
    XlPy/Spectra/mzml
    _________________

    Parser for the open data format for raw scan data.
    Schema:
        http://www.peptideatlas.org/tmp/mzML1.1.0.html

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# Code inspired and partly guided from mMass by Martin Strohalm.
# XL Discoverer is not affiliated with or endorsed by mMass.
#     Copyright (C) 2008-2011 Martin Strohalm <www.mmass.org>
# License can be found in licenses/mMass.txt

# load modules
import base64
import struct
import xml.sax
import zlib

import numpy as np

from xldlib.definitions import re, ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger
from xldlib.xlpy.tools import peak_picking

# load objects/functions
from collections import namedtuple


# OBJECTS
# -------
BinaryData = namedtuple("BinaryData", "data precision compression")


# REGEXP
# ------
MZML_SCAN = re.compile(r'scan=([0-9]+)')


# HELPERS
# -------


@logger.init('scans', level='DEBUG')
class Start(base.BaseObject):
    '''Utilities for processing data from XML start elements'''

    def __init__(self, group):
        super(Start, self).__init__()

        self.group = group
        self.source = self.app.discovererthread

    def spectrum(self, attrs):
        '''Starts the scan data and inits the holder'''

        self.set_newscan(attrs)

        peaks = attrs.get('defaultArrayLength')
        if peaks is not None:
            self.scan.setattr('peaks_count', int(peaks))

    def precursor(self, attrs):
        '''Starts the precursor data for the given scan at MS2+ levels'''

        spectrum_ref = attrs.get('spectrumRef', False)
        if spectrum_ref:
            precursor_num = self.get_scan_number(spectrum_ref)
            self.scan.setattr('precursor_num', precursor_num)

    def precursor_params(self, attrs):
        '''Processes information for the precursor scan.'''

        name = attrs.get('name', '')
        value = attrs.get('value', '')
        if name == 'selected ion m/z' and value is not None:
            self.scan.setattr('precursor_mz', float(value))

        elif name == 'intensity' and value is not None:
            self.scan.setattr('precursor_intensity', float(value))

        elif name == 'possible charge state' and value is not None:
            self.scan.setattr('precursor_z', int(value))

        elif name == 'charge state' and value is not None:
            self.scan.setattr('precursor_z', int(value))

    def process_spectrum_params(self, attrs):
        '''
        Adds data based from spectrum params.
        :
            attrs -- element attributes
            name -- element name
            value -- element value
        '''

        name = attrs.get('name', '')
        value = attrs.get('value', '')

        # data type
        if name == 'centroid spectrum':
            self.scan.setattr('spectrum_type', 'centroided')
        elif name == 'profile spectrum':
            self.scan.setattr('spectrum_type', 'profile')
        # MS level
        elif name == 'ms level' and value is not None:
            self.scan.setattr('ms_level', int(value))
        # polarity
        elif name == 'positive scan':
            self.scan.setattr('polarity', 'positive')
        elif name == 'negative scan':
            self.scan.setattr('polarity', 'negative')
        # total ion current
        elif name == 'total ion current' and value is not None:
            self.scan.setattr('total_ion_current', max(0.0, float(value)))
        # base peak
        elif name == 'base peak m/z' and value is not None:
            self.scan.setattr('basepeak_mz', float(value))
        elif name == 'base peak intensity' and value is not None:
            self.scan.setattr('basepeak_intensity', max(0.0, float(value)))
        # mass range
        elif name == 'lowest observed m/z' and value is not None:
            self.scan.setattr('low_mz', float(value))
        elif name == 'highest observed m/z' and value is not None:
            self.scan.setattr('high_mz', float(value))
        # retention time
        elif name == 'scan start time' and value is not None:
            retention_time = self.get_retentiontime(attrs, value)
            self.scan.setattr('retention_time', retention_time)

    #     GETTERS

    @staticmethod
    @logger.except_error((TypeError, AttributeError))
    def get_scan_number(scan_string):
        '''
        Extracts scan ID based on re.match.
        Regex and code used from Martin Strohalm:
        Copyright (C) 2005-2013 Martin Strohalm <www.mmass.org>.
        '''

        match = MZML_SCAN.search(scan_string)
        if not match:
            return None

        return int(match.group(1))

    @staticmethod
    def get_retentiontime(attrs, value):
        '''Extracts the retention time and normalizes for time units'''

        if attrs.get('unitName', '') == 'minute':
            return float(value)
        elif attrs.get('unitName', '') == 'second':
            return float(value) / 60
        else:
            return float(value)

    #     SETTERS

    def set_newscan(self, attrs):
        '''Sets a new scan group for the startElements'''

        scan_id = attrs['id']
        num = self.get_scan_number(scan_id)
        self.scan = self.group.newscan(num)
        self.scan.setattr('num', num)


# DATA
# ----

ARRAYS = [
    'mz',
    'intensity'
]


class End(base.BaseObject):
    '''Utilities for processing data from XML end elements'''

    def __init__(self):
        super(End, self).__init__()

        self.source = self.app.discovererthread

        self.set_parameters()

    def spectrum(self, scan, mzs, intensity):
        '''Ends and processes spectrum data and Decodes peak lists.'''

        if self.get_storespectra(scan):
            arrays = self.get_decoded_scans(scan, mzs, intensity)
            if scan.getattr('spectrum_type') != 'centroided':
                arrays = peak_picking.centroid_scan(*arrays)

            for key, array in ZIP(ARRAYS, arrays):
                scan.create_array(key, obj=array)

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

    def get_decoded_scans(self, group, mzs, intensity):
        '''Unpacks m/z-int base64 encoded data to lists.'''

        for index, binarydata in enumerate((mzs, intensity)):
            data = self.get_decoded_b64(binarydata)
            if not data:
                yield np.array([])
                continue

            # unpack struct
            prec = ['f', 'd'][binarydata.precision == 64]
            byte = defaults.DEFAULTS['byte_order']['little']
            count = len(data) // struct.calcsize(byte + prec)
            values = struct.unpack(byte + prec*count, data)
            yield np.array(values)

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

        if name == 'spectrum':
            self._spectrum = True
            self.start.spectrum(attrs)
            self.scan = self.start.scan

        elif name == 'precursor' and self._spectrum:
            self._precursor = True
            self.start.precursor(attrs)

        elif name == 'binaryDataArray' and self._spectrum:
            self._binary_data_array = True
            self._tmp_binary_data = []

        elif name == 'binary' and self._binary_data_array:
            self._binary_data = True

        elif name == 'cvParam' and self._precursor:
            self.start.precursor_params(attrs)

        elif name == 'cvParam':
            if self._binary_data_array:
                self.set_binary_data(attrs)

            elif self._spectrum:
                self.start.process_spectrum_params(attrs)

    def endElement(self, name):
        '''Element ended.'''

        if name == 'spectrum':
            self._spectrum = False
            self.end.spectrum(self.scan, self.mz, self.intensity)
            del self.scan, self.mz, self.intensity

        elif name == 'precursor':
            self._precursor = False

        elif name == 'binaryDataArray' and self._spectrum:
            self._binary_data_array = False
            self.process_binary_data()

        elif name == 'binary':
            self._binary_data = False

    def characters(self, text):
        '''Grab characters.'''

        if self._binary_data:
            self._tmp_binary_data.append(text)

    #     SETTERS

    def set_defaults(self):
        '''Sets the default values for scan grouping in the sax parser'''

        self.scan = None
        self._spectrum = False
        self._precursor = False
        self._binary_data_array = False
        self._binary_data = False
        self._tmp_binary_data = None
        self._tmp_precision = None
        self._tmp_compression = None
        self._tmp_array_type = None

    def set_binary_data(self, attrs):
        '''Processes the binary data.'''

        # precision
        name = attrs.get('name', '')
        if name == '64-bit float':
            self._tmp_precision = 64
        elif name == '32-bit float':
            self._tmp_precision = 32
        # compression
        elif name == 'zlib compression':
            self._tmp_compression = 'zlib'
        elif name == 'no compression':
            self._tmp_compression = None
        # array type
        elif name == 'm/z array':
            self._tmp_array_type = 'mzArray'
        elif name == 'intensity array':
            self._tmp_array_type = 'intArray'

    #     PROCESSORS

    def process_binary_data(self):
        '''Process the binary data elements when they end'''

        data = ''.join(self._tmp_binary_data)
        values = BinaryData(data, self._tmp_precision, self._tmp_compression)

        if self._tmp_array_type == 'mzArray':
            self.mz = values

        elif self._tmp_array_type == 'intArray':
            self.intensity = values

        self._tmp_binary_data = None
        self._tmp_precision = None
        self._tmp_compression = None


# PARSER
# ------


@logger.init('scans', level='DEBUG')
class ParseXml(base.BaseObject):
    '''
    Processes the XML-like open source data-format, common
    with the TransProteomic Pipeline.'''

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
