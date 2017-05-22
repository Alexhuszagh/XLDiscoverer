'''
    XlPy/Raw/Thermo_Finnigan/file
    _____________________________

    Parser for Thermo Raw files, using their XRawFile2.dll

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import ctypes
import sys

# load objects/functions
from thermo_finnigan.api import ThermoFinniganApi
from .scan import ScanHandler

assert sys.platform == 'win32'

class RawFile(object):
    '''
    Initializes a raw file instance to parse scans, attempting various
    COM CLSIDs for the Thermo MSFileReader.
    '''

    _ms1 = None
    _ms2 = {}

    def __init__(self, fileobj, grp, source):
        '''Init inst on construction of a successful rawfile COM object'''

        self.path = fileobj.name
        fileobj.close()
        self.grp = grp
        self.source = source

        self.ms_file_reader = ThermoFinniganApi(self.path)
        self.ms_file_reader.set_current_controller(0, 1)

        super(RawFile, self).__init__()

    def extract_data(self):
        '''Iter over all scan numbers and process scan data'''

        first_scan = self.ms_file_reader.get_first_spectrum_number()
        last_scan = self.ms_file_reader.get_last_spectrum_number()
        for scan in range(first_scan, last_scan + 1):
            ScanHandler(scan, self)
