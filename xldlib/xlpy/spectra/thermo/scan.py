'''
    XlPy/Raw/Thermo_Finnigan/scan
    _____________________________

    Extract data from a given scan into Pythonic types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import comtypes
import ctypes

# load objects/functions
from libs.definitions import re


class ScanHandler(object):
    '''
    Extracts centroided peak lists and spectral metadata (including scan
    hierarchy, etc.).

    Method functions are described by general utility, and then with the
    C types and functions annotated to simplify the C call structure.

    All return types are longs, with a return of 0 meaning success.
    Python returns abbreviated error codes (hex value -> 1 digit integer),
    so the error codes are not enumerated here.
    '''

    # scan extraction
    ms2_header = re.compile(r'.* Full ms2 (?P<mz>\d+\.\d+)@'
                            r'cid(?P<cid>\d+\.\d+) .*')
    ms3_header = re.compile(r'.* Full ms3 (?P<prec_mz>\d+\.\d+)@'
                            r'cid(?P<prec_cid>\d+\.\d+) '
                            r'(?P<prod_mz>\d+\.\d+)@'
                            r'cid(?P<prod_cid>\d+\.\d+) .*')

    # default settings
    _centroided = True

    def __init__(self, scan, parent):
        super(ScanHandler, self).__init__()

        self.rawfile = parent.rawfile
        self.grp = parent.grp
        self.parent = parent
        # int is fine, no long required
        self.scan_num = scan

        self.ms_level = self._ms_level()
        self.scan_filter = self.get_filter_for_scan_num().value

        if self.ms_level == 1:
            self.parent._ms1 = self.scan_num
            self.parent._ms2.clear()
        elif self.ms_level == 2:
            mz_str = self.ms2_header.match(self.scan_filter).group('mz')
            self.parent._ms2[mz_str] = scan
            self.precursor = self.parent._ms1

        else:
            match = self.ms3_header.match(self.scan_filter)
            prec_mz = match.group('prec_mz')
            self.precursor = self.parent._ms2[prec_mz]

    def set_data(self):
        '''Stores all the data into the group if the right MS level'''

        grp = self.grp.create_group(None)

        grp.attrs['num'] = self.scan_num
        grp.attrs['retention_time'] = self.retention_time()
        grp.attrs['precursor_num'] = None
        grp.attrs['file'] = None
        grp.attrs['precursor_mz'] = None
        grp.attrs['precursor_intensity'] = None
        grp.attrs['precursor_z'] = None

    def retention_time(self):
        '''
        Returns the current retention time from the scan
        :
            RTFromScanNum(long nScanNumber, double FAR* pdRT)

            -> 0.37657
        '''

        retention_time = ctypes.c_double()
        self.rawfile.RTFromScanNum(self.scan_num, retention_time)
        return retention_time.value

    def _ms_level(self):
        '''
        Returns the MS level for the scan
        :
            GetMSOrderForScanNum(long nScanNumber,
                long FAR *pnMassOrder)

            -> 1
        '''

        try:
            assert self.parent.raw_interface > 3
            ms_level = ctypes.c_long()
            self.rawfile.GetMSOrderForScanNum(self.scan_num, ms_level)
            return ms_level.value

        except AssertionError:
            # for interface versions 3 and below
            # grab index + len('ms') + 1
            index = self.scan_filter.index('ms') + 3
            try:
                ms_level = int(index)
            except ValueError:
                ms_level = 1
            return ms_level

    def get_precursor_mz(self):
        '''
        Returns the precursor mass information, requires interface > 4
        :
            GetPrecursorMassForScanNum(long nScanNumber,
                long nMSOrder,
                double FAR *pdPrecursorMass)
        '''

        mass = ctypes.c_double()
        self.rawfile.GetPrecursorMassForScanNum(
            self.scan_num,
            self.ms_level,
            mass
        )
        return mass.value

    def get_precursor_charge(self):
        pass

    def scan_lists(self):
        '''
        Returns the mass and intensity scan lists from a given scan
        :
            GetMassListFromScanNum(long FAR* pnScanNumber, LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)

            -> np.array([401.66, ...]), np.array([4131.76, ...])
        '''

        num = ctypes.c_long(self.scan_num)
        null_filter = comtypes.BSTR()
        cutoff_none = ctypes.c_long(0)
        cutoff_value = ctypes.c_long()
        max_peaks = ctypes.c_long()
        centroided = self._centroided
        peak_width = ctypes.c_double(0)
        mass_list = comtypes.automation.VARIANT()
        peak_flags = comtypes.automation.VARIANT()
        size = ctypes.c_long()

        self.rawfile.GetMassListFromScanNum(
            num,
            null_filter,
            cutoff_none,
            cutoff_value,
            max_peaks,
            centroided,
            peak_width,
            mass_list,
            peak_flags,
            size
        )

        with comtypes.safearray.safearray_as_ndarray:
            mzs, intensity = mass_list.value
            return mzs, intensity
