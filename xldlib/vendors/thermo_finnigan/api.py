'''
    Vendors/Thermo_Finnigan/api
    ___________________________

    Extract data from a given scan into Pythonic types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import comtypes
import comtypes.client
import ctypes
import datetime
import os
import six

from . import compound_types
from xldlib.utils import decorators
from xldlib import win32

# load objects/functions
from xldlib.definitions import NoneType, re

# Constants

VERSIONS = [
    # CLSID, IID
    [
        # Version 2.1
        '{5FE970B2-29C3-11D3-811D-00104B304896}',
        '{5FE970B1-29C3-11D3-811D-00104B304896}'
    ],
    [
        # Version 2.2.61.0
        '{1D23188D-53FE-4C25-B032-DC70ACDBDC02}',
        '{11B488A0-69B1-41FC-A660-FE8DF2A31F5B}'

    ]
]


class ThermoFinniganApi(object):
    '''
    Provides methods to extract data directly from a ThermoFinnigan raw
    file, without complication for C-types, etc.
    '''

    # Constants
    S_OK = 0

    # NULL initialized attributes
    filename = None

    # Utilities
    _raw_interface = re.compile(r'POINTER\(IXRawfile(?P<ver>\d)\)')

    def __init__(self, path=None):
        super(ThermoFinniganApi, self).__init__()

        for CLSID, IID in VERSIONS:
            try:
                self.msfile_lib = comtypes.client.CreateObject(CLSID)
            except OSError:
                # caught windows error
                pass

        # ensure properly initialized and get raw library version
        match = self._raw_interface.match(self.msfile_lib.__class__.__name__)
        self.raw_interface = int(match.group('ver'))
        if path is not None:
            self.open(path)

    # ------------------
    #     FUNCTIONS
    # ------------------

    #       I/O

    @decorators.accepts(object, six.string_types)
    def open(self, path):
        '''
        Opens a raw file using the Thermo MSFileReader library
        :
            Open(LPCTSTR szFileName)
        '''

        res = self.msfile_lib.open(path)
        assert res == self.S_OK

        self.filename = os.path.basename(path)

    @decorators.accepts(object)
    def close(self):
        '''
        Opens a raw file using the Thermo MSFileReader library
        :
            Open(LPCTSTR szFileName)
        '''

        res = self.msfile_lib.Close()
        assert res == self.S_OK, res

    @decorators.accepts(object)
    def refresh_view_of_file(self):
        '''
        Refreshes the file view faster than closing and re-opening
        :
            RefreshViewOfFile()
        '''

        res = self.msfile_lib.RefreshViewOfFile()
        assert res == self.S_OK, res

    #    FILE ATTRS

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_filename(self):
        '''
        Returns the path to an open raw file.
        :
            GetFileName(BSTR FAR* pbstrFileName)

            -> 'C:\\data\\file.raw'
        '''

        filename = comtypes.BSTR()
        res = self.msfile_lib.GetFileName(filename)
        assert res == self.S_OK, res

        return filename.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_creator_id(self):
        '''
        Returns the username of the user during raw file creation
        :
            GetCreatorID(BSTR FAR* pbstrCreatorID)

            -> 'creator_name'
        '''

        creator_id = comtypes.BSTR()
        res = self.msfile_lib.GetCreatorID(creator_id)
        assert res == self.S_OK, res

        return creator_id.value

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_version_number(self):
        '''
        Returns version information for the file format
        :
            GetVersionNumber(long FAR* pnVersion)

            -> 66
        '''

        version = ctypes.c_long()
        res = self.msfile_lib.GetVersionNumber(version)
        assert res == self.S_OK, res

        return version.value

    @decorators.accepts(object)
    @decorators.returns(datetime.datetime)
    def get_creation_date(self):
        '''
        Returns date of file creation
        :
             GetCreationDate(DATE FAR* pCreationDate)

             -> datetime.datetime(2015, 7, 17, 19, 15, 18)
        '''

        date = ctypes.c_double()
        res = self.msfile_lib.GetCreationDate(date)
        assert res == self.S_OK, res

        return win32.oadate(date)

    @decorators.accepts(object)
    @decorators.returns(bool)
    def is_new_file(self):
        '''
        Returns if the file has been previously saved.
        :
            IsNewFile(BOOL FAR* pbIsNewFile)

            -> False
        '''

        is_new = ctypes.c_long()
        res = self.msfile_lib.IsNewFile(is_new)
        assert res == self.S_OK, res

        return bool(is_new.value)

    #  ERROR HANDLING

    @decorators.accepts(object)
    @decorators.returns(bool)
    def is_error(self):
        '''
        Returns a flag for the error state of the raw file
        :

            IsError(BOOL FAR* pbIsError)

            -> False
        '''

        error = ctypes.c_long()
        res = self.msfile_lib.isError(error)
        assert res == self.S_OK, res

        return bool(error.value)

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_error_code(self):
        '''
        Returns an error code for the state of the raw file.
        :
            GetErrorCode(long FAR* pnErrorCode)

            -> 0
        '''

        error = ctypes.c_long()
        res = self.msfile_lib.GetErrorCode(error)
        assert res == self.S_OK, res

        return error.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_error_message(self):
        '''
        Returns the current error message for the raw file.
        :
            GetErrorMessage(BSTR FAR* pbstrErrorMessage)

            -> u''
        '''

        message = comtypes.BSTR()
        res = self.msfile_lib.GetErrorMessage(message)
        assert res == self.S_OK, res

        return message.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_warning_message(self):
        '''
        Returns the current warning message for the raw file.
        :
            GetWarningMessage(BSTR FAR* pbstrWarningMessage)

            -> u''
        '''

        message = comtypes.BSTR()
        res = self.msfile_lib.GetWarningMessage(message)
        assert res == self.S_OK, res

        return message.value

    #    SEQUENCES

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_seq_row_number(self):
        '''
        Returns the sequence row number, starting at 1 (0 if unset)
        :
            GetSeqRowNumber(long FAR* pnSeqRowNumber)

            -> 1
        '''

        row = ctypes.c_long()
        res = self.msfile_lib.GetSeqRowNumber(row)
        assert res == self.S_OK, res

        return row.value

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_seq_row_sample_type(self):
        '''
        Returns the integer represention of the sample type, enumerated
        in thermo_finnigan.lib_def.Sample_Type
        :
             GetSeqRowSampleType(long FAR* pnSampleType)

             -> 0
        '''

        type_ = ctypes.c_long()
        res = self.msfile_lib.GetSeqRowSampleType(type_)
        assert res == self.S_OK, res

        return type_.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_data_path(self):
        '''
        Returns path to raw file acquisition directory
        :
            GetSeqRowDataPath(BSTR FAR* pbstrDataPath)

            -> 'C:\\data'
        '''

        path = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowDataPath(path)
        assert res == self.S_OK, res

        return path.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_raw_filename(self):
        '''
        Returns the original name for the acquired raw file.
        :
             GetSeqRowRawFileName(BSTR FAR* pbstrRawFileName)

             -> 'C:\\data\\file.raw'
        '''

        filename = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowRawFileName(filename)
        assert res == self.S_OK, res

        return filename.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_sample_name(self):
        '''
        Returns the sample name descriptor.
        :
             GetSeqRowSampleName(BSTR FAR* pbstrSampleName)

             -> ''
        '''

        sample_name = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowSampleName(sample_name)
        assert res == self.S_OK, res

        return sample_name.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_sample_id(self):
        '''
        Returns the sample identifier
        :
            GetSeqRowSampleID(BSTR FAR* pbstrSampleID)

            -> '20 fmol'
        '''

        sample_id = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowSampleID(sample_id)
        assert res == self.S_OK, res

        return sample_id.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_comment(self):
        '''
        Returns entered comment descriptor for raw file.
        :
            GetSeqRowComment(BSTR FAR* pbstrComment)

            -> ''
        '''

        comment = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowComment(comment)
        assert res == self.S_OK, res

        return comment.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_level_name(self):
        '''
        Returns level name specified for sequence acquisition.
        :
            GetSeqRowLevelName(BSTR FAR* pbstrLevelName)

            -> ''
        '''

        level_name = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowLevelName(level_name)
        assert res == self.S_OK, res

        return level_name.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_user_text(self):
        '''
        Returns user text specified for sequence acquisition.
        :
            GetSeqRowUserText(long nIndex, BSTR FAR* pbstrUserText)

            -> ''
        '''

        user_text = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowUserText(user_text)
        assert res == self.S_OK, res

        return user_text.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_instrument_method(self):
        '''
        Returns instrument method specified for sequence acquisition.
        :
            GetSeqRowInstrumentMethod(BSTR FAR* pbstrInstrumentMethod)

            -> 'C:\\path\\to\\method.meth'
        '''

        instrument_method = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowInstrumentMethod(instrument_method)
        assert res == self.S_OK, res

        return instrument_method.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_processing_method(self):
        '''
        Returns processing method specified for sequence acquisition.
        :
            GetSeqRowProcessingMethod(BSTR FAR* pbstrProcessingMethod))

            -> ''
        '''

        processing_method = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowProcessingMethod(processing_method)
        assert res == self.S_OK, res

        return processing_method.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_set_row_calibration_file(self):
        '''
        Returns full path to the calibration file for sequence acquisition
        :
            GetSetRowCalibrationFile(BSTR FAR* pbstrCalibrationFile)

            -> ''
        '''

        calibration_file = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowCalibrationFile(calibration_file)
        assert res == self.S_OK, res

        return calibration_file.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_vial(self):
        '''
        Returns well number for file acquisition.
        :
            GetSeqRowVial(BSTR FAR* pbstrVial)

            -> 1:E3
        '''

        well_number = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowVial(well_number)
        assert res == self.S_OK, res

        return well_number.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_injection_volume(self):
        '''
        Returns the injection volume for sequence acquisition.
        :
            GetSeqRowInjectionVolume(BSTR FAR* pbstrVial)

            -> 'C:\\path\\to\\method.meth'
        '''

        volume = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowInstrumentMethod(volume)
        assert res == self.S_OK, res

        return volume.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_seq_row_sample_weight(self):
        '''
        Returns the sample weight for sequence acquisition.
        :
            GetSeqRowSampleWeight(double FAR* pdSampleWt)

            -> 0.0
        '''

        sample_weight = ctypes.c_double()
        res = self.msfile_lib.GetSeqRowSampleWeight(sample_weight)
        assert res == self.S_OK, res

        return sample_weight.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_seq_row_sample_volume(self):
        '''
        Returns the sample volume for sequence acquisition.
        :
            GetSeqRowSampleVolume(double FAR* pdSampleVolume)

            -> 0.0
        '''

        sample_volume = ctypes.c_double()
        res = self.msfile_lib.GetSeqRowSampleVolume(sample_volume)
        assert res == self.S_OK, res

        return sample_volume.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_seq_row_istd_amount(self):
        '''
        Returns the sample istd correction for sequence acquisition.
        :
            GetSeqRowISTDAmount(double FAR* pdISTDAmount)

            -> 0.0
        '''

        istd_amount = ctypes.c_double()
        res = self.msfile_lib.GetSeqRowISTDAmount(istd_amount)
        assert res == self.S_OK, res

        return istd_amount.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_seq_row_dilution_factor(self):
        '''
        Returns the sample dilution factor for sequence acquisition.
        :
            GetSeqRowDilutionFactor(double FAR* pdDilutionFactor)

            -> 1.0
        '''

        dilution_factor = ctypes.c_double()
        res = self.msfile_lib.GetSeqRowDilutionFactor(dilution_factor)
        assert res == self.S_OK, res

        return dilution_factor.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.string_types)
    def get_seq_row_user_label(self, n_index):
        '''
        Returns the sample user label at the given index for sequence
        acquisition.
        :
            GetSeqRowUserLabel(long nIndex, BSTR FAR* pbstrUserLabel)

            -> 'Client'
        '''

        user_label = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowUserLabel(n_index, user_label)
        assert res == self.S_OK, res

        return user_label.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.string_types)
    def get_seq_row_user_text_ex(self, n_index):
        '''
        Returns the user text field at the given index for sequence acquisition
        :
            GetSeqRowUserTextEx(long nIndex, BSTR FAR* pbstrUserText)

            -> ''
        '''

        user_text_ex = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowUserTextEx(n_index, user_text_ex)
        assert res == self.S_OK, res

        return user_text_ex.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_barcode(self):
        '''
        Returns the barcode for sequence acquisition
        :
            GetSeqRowBarcode(BSTR FAR* pbstrBarcode)

            -> ''
        '''

        barcode = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowBarcode(barcode)
        assert res == self.S_OK, res

        return barcode.value

    @decorators.accepts(object)
    @decorators.returns(six.string_types)
    def get_seq_row_barcode_status(self):
        '''
        Returns the barcode status for the sequence acquisition
        :
             GetSeqRowBarcodeStatus(long* pnStatus)

             -> ''
        '''

        barcode_status = comtypes.BSTR()
        res = self.msfile_lib.GetSeqRowBarcode(barcode_status)
        assert res == self.S_OK, res

        return barcode_status.value or ''

    #    ACQUSITION

    @decorators.accepts(object)
    @decorators.returns(bool)
    def in_acquisition(self):
        '''
        Returns if the file is currently being acquired
        :
            InAcquisition(BOOL FAR* pbInAcquisition)

            -> False
        '''

        acquiring = ctypes.c_long()
        res = self.msfile_lib.InAcquisition(acquiring)
        assert res == self.S_OK, res

        return bool(acquiring.value)

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_number_of_controllers(self):
        '''
        Returns the number of controllers within the raw file
        :
            GetNumberOfControllers(long FAR* pnNumControllers)

            -> 1
        '''

        controllers = ctypes.c_long()
        res = self.msfile_lib.GetNumberOfControllers(controllers)
        assert res == self.S_OK, res

        return controllers.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_controllers_of_type(self, n_controller_type):
        '''
        Returns the number of controllers of a given type within the raw file
        See thermo_finnigan.lib_def.Controller_Types for enumerated
        controller types.
        :
            GetNumberOfControllersOfType(long nControllerType,
                long FAR* pnNumControllersOfType)

            -> 1
        '''

        controllers = ctypes.c_long()
        res = self.msfile_lib.GetNumberOfControllersOfType(
            n_controller_type,
            controllers
        )
        assert res == self.S_OK, res

        return controllers.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_controller_type(self, n_index):
        '''
        Returns the controller type at a given index.
        See thermo_finnigan.lib_def.Controller_Types for enumerated
        controller types.
        :
            GetControllerType(long nIndex, long FAR* pnControllerType)

            -> 0
        '''

        controller_type = ctypes.c_long()
        res = self.msfile_lib.GetControllerType(n_index, controller_type)
        assert res == self.S_OK, res

        return controller_type.value

    @decorators.accepts(object, six.integer_types, six.integer_types)
    def set_current_controller(self, n_controller_type, n_controller_number):
        '''
        Sets the current controller for the MSFileReader, msfile_lib will be
        read-only prior to setting controllers.
        :
            SetCurrentController(long nControllerType, long nControllerNumber)
        '''

        res = self.msfile_lib.SetCurrentController(
            n_controller_type,
            n_controller_number
        )
        assert res == self.S_OK, res

    @decorators.accepts(object)
    @decorators.returns(tuple)
    def get_current_controller(self):
        '''
        Returns the current controller for the MSFileReader.
        :
            SetCurrentController(long nControllerType, long nControllerNumber)

            -> (0, 1)
        '''

        n_controller_type = ctypes.c_long()
        n_controller_number = ctypes.c_long()

        res = self.msfile_lib.GetCurrentController(
            n_controller_type,
            n_controller_number
        )
        assert res == self.S_OK, res

        return n_controller_type.value, n_controller_number.value

    #    RUNTIME

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_num_spectra(self):
        '''
        Returns the total number of spectra acquired by the controller.
        :
            GetNumSpectra(long FAR* pnNumberOfSpectra)

            -> 10543
        '''

        spectra = ctypes.c_long()
        res = self.msfile_lib.GetNumSpectra(spectra)
        assert res == self.S_OK, res

        return spectra.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_mass_resolution(self):
        '''
        Returns the mass resolution acquired by the controller.
        :
             GetMassResolution(double FAR* pdMassResolution)

             -> 0.5
        '''

        mass_resolution = ctypes.c_double()
        res = self.msfile_lib.GetMassResolution(mass_resolution)
        assert res == self.S_OK, res

        return mass_resolution.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_expected_runtime(self):
        '''
        Returns the expected runtime acquired by the controller.
        :
             GetExpectedRunTime(double FAR* pdExpectedRunTime)

             -> 60.0
        '''

        expected_runtime = ctypes.c_double()
        res = self.msfile_lib.GetExpectedRunTime(expected_runtime)
        assert res == self.S_OK, res

        return expected_runtime.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_low_mass(self):
        '''
        Returns lowest mass recorded by the controller.
        :
             GetLowMass(double FAR* pdLowMass)

             -> 106.0
        '''

        low_mass = ctypes.c_double()
        res = self.msfile_lib.GetLowMass(low_mass)
        assert res == self.S_OK, res

        return low_mass.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_high_mass(self):
        '''
        Returns highest mass recorded by the controller.
        :
            GetHighMass(double FAR* pdHighMass)

            -> 2000.0
        '''

        high_mass = ctypes.c_double()
        res = self.msfile_lib.GetHighMass(high_mass)
        assert res == self.S_OK, res

        return high_mass.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_start_time(self):
        '''
        Returns the start time recorded by the controller.
        :
            GetStartTime(double FAR* pdStartTime)

            -> 0.0015082629333333334
        '''

        start_time = ctypes.c_double()
        res = self.msfile_lib.GetStartTime(start_time)
        assert res == self.S_OK, res

        return start_time.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_end_time(self):
        '''
        Returns the end time recorded by the controller.
        :
            GetEndTime(double FAR* pdEndTime)

            -> 60.00236448693333
        '''

        end_time = ctypes.c_double()
        res = self.msfile_lib.GetEndTime(end_time)
        assert res == self.S_OK, res

        return end_time.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_max_integrated_intensity(self):
        '''
        Returns the max integrated intensity for the controller
        :
            GetMaxIntegratedIntensity(double FAR* pdMaxIntegIntensity)

            -> 2389772288.0
        '''

        max_intensity = ctypes.c_double()
        res = self.msfile_lib.GetMaxIntegratedIntensity(max_intensity)
        assert res == self.S_OK, res

        return max_intensity.value

    @decorators.accepts(object)
    @decorators.returns(float)
    def get_max_intensity(self):
        '''
        Returns the max intensity for the controller
        :
             GetMaxIntensity(long FAR* pnMaxIntensity)

             -> 2389772288.0
        '''

        max_intensity = ctypes.c_double()
        res = self.msfile_lib.GetMaxIntegratedIntensity(max_intensity)
        assert res == self.S_OK, res

        return max_intensity.value

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_first_spectrum_number(self):
        '''
        Returns the first scan recorded by the controller.
        :
             GetFirstSpectrumNumber(long FAR* pnFirstSpectrum)

             -> 1
        '''

        first_scan = ctypes.c_long()
        res = self.msfile_lib.GetFirstSpectrumNumber(first_scan)
        assert res == self.S_OK, res

        return first_scan.value

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_last_spectrum_number(self):
        '''
        Returns the last scan recorded by the controller.
        :
             GetLastSpectrumNumber(long FAR* pnLastSpectrum)

             -> 10543
        '''

        last_scan = ctypes.c_long()
        res = self.msfile_lib.GetLastSpectrumNumber(last_scan)
        assert res == self.S_OK, res

        return last_scan.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(tuple)
    def get_mass_precision_estimate(self, n_scan):
        '''
        Returns the mass precision for a given scan.
        :
             GetMassPrecisionEstimate(long nScanNumber, VARIANT *pvarMassList,
                long *pnArraySize)

            -> array([1.4666e+03, ...]), 1130
        '''

        mass_list = comtypes.automation.VARIANT()
        array_size = ctypes.c_long()

        res = self.msfile_lib.GetMassPrecisionEstimate(n_scan, mass_list, array_size)
        assert res == self.S_OK, res

        with comtypes.safearray.safearray_as_ndarray:
            return mass_list.value, array_size.value

    #     FOR SCAN

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.string_types)
    def get_filter_for_scan_num(self, n_scan):
        '''
        Returns the scan header filtering information
        :
            GetFilterForScanNum(long nScanNumber, BSTR FAR* pbstrFilter)

            -> u'ITMS + c NSI d Full ms3 409.4413@cid35.00 368.5263@'
                'cid35.00 [200.0000-2000.0000]'
        '''

        string = comtypes.BSTR()
        res = self.msfile_lib.GetFilterForScanNum(n_scan, string)
        assert res == self.S_OK, res

        return string.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(bool)
    def is_profile_scan_for_scan_num(self, n_scan):
        '''
        Returns if the scan data is profile for the scan number
        :
            IsProfileScanForScanNum(long nScanNumber, long pbIsProfileScan)

            -> False
        '''

        profile = ctypes.c_long()
        res = self.msfile_lib.IsProfileScanForScanNum(n_scan, profile)
        assert res == self.S_OK, res

        return bool(profile.value)

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(bool)
    def is_centroid_scan_for_scan_num(self, n_scan):
        '''
        Returns if the scan data is centroided for the scan number
        :
             IsCentroidScanForScanNum(long nScanNumber, long pbIsCentroidScan)

             -> False
        '''

        centroided = ctypes.c_long()
        res = self.msfile_lib.IsProfileScanForScanNum(n_scan, centroided)
        assert res == self.S_OK, res

        return bool(centroided.value)

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(compound_types.ScanHeaderInfo)
    def get_scan_header_info_for_scan_num(self, n_scan):
        '''
        Returns the extracted scan header from a given scan
        :
             GetScanHeaderInfoForScanNum(long nScanNumber, long FAR*
                pnNumPackets, double FAR*
                pdStartTime,
                double FAR* pdLowMass,
                double FAR* pdHighMass, double FAR*
                pdTIC, double FAR* pdBasePeakMass,
                double FAR* pdBasePeakIntensity,
                long FAR* pnNumChannels,
                long pbUniformTime,
                double FAR* pdFrequency)

            -> ScanHeaderInfo(num_packets=59196,
                              start_time=0.0015082629333333334,
                              low_mass=400.0,
                              high_mass=1600.0,
                              total_ion_count=8645031.0,
                              base_peak_mass=445.1192932128906,
                              base_peak_intensity=1311619.375,
                              num_channels=0,
                              uniform_time=0,
                              frequency=0.0)
        '''

        num_packets = ctypes.c_long()
        start_time = ctypes.c_double()
        low_mass = ctypes.c_double()
        high_mass = ctypes.c_double()
        total_ion_count = ctypes.c_double()
        base_peak_mass = ctypes.c_double()
        base_peak_intensity = ctypes.c_double()
        num_channels = ctypes.c_long()
        uniform_time = ctypes.c_long()
        frequency = ctypes.c_double()

        res = self.msfile_lib.GetScanHeaderInfoForScanNum(
            n_scan,
            num_packets,
            start_time,
            low_mass,
            high_mass,
            total_ion_count,
            base_peak_mass,
            base_peak_intensity,
            num_channels,
            uniform_time,
            frequency
        )
        assert res == self.S_OK, res

        return compound_types.ScanHeaderInfo(
            num_packets.value,
            start_time.value,
            low_mass.value,
            high_mass.value,
            total_ion_count.value,
            base_peak_mass.value,
            base_peak_intensity.value,
            num_channels.value,
            uniform_time.value,
            frequency.value
        )

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(float)
    def get_isolation_width_for_scan_num(self, n_scan):
        '''
        Returns the isolation width for the MS scan
        :
            GetIsolationWidthForScanNum(long nScanNumber, long nMSOrder,
                double FAR *pdIsolationWidth)

            -> 2.0
        '''

        ms_order = ctypes.c_long()
        isolation_width = ctypes.c_double()

        res = self.msfile_lib.GetIsolationWidthForScanNum(
            n_scan,
            ms_order,
            isolation_width
        )
        assert res == self.S_OK, res

        return isolation_width.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(float)
    def get_collision_energy_for_scan_num(self, n_scan):
        '''
        Returns the collision for the MS scan
        :
            GetCollisionEnergyForScanNum(long nScanNumber, long nMSOrder,
                double FAR *pdCollisionEnergy)

            -> 2.0
        '''

        ms_order = ctypes.c_long()
        collision_energy = ctypes.c_double()

        res = self.msfile_lib.GetIsolationWidthForScanNum(
            n_scan,
            ms_order,
            collision_energy
        )
        assert res == self.S_OK, res

        return collision_energy.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(compound_types.PrecursorRange)
    def get_precursor_range_for_scan_num(self, n_scan):
        '''
        Returns the first and last precursor mass for the scan num
        :
            GetPrecursorRangeForScanNum(long nScanNumber, long nMSOrder,
                double FAR
                *pdFirstPrecursorMass, double FAR *pdLastPrecursorMass, BOOL
                FAR *pbIsValid)

            ->
        '''

        # GET THE MS ORDER
        # ms_order = ctypes.c_long()
        first_precursor_mass = ctypes.c_double()
        last_precursor_mass = ctypes.c_double()
        valid = ctypes.c_long()

        res = self.msfile_lib.GetPrecursorRangeForScanNum(
            n_scan,
            ms_order,
            first_precursor_mass,
            last_precursor_mass,
            valid
        )
        assert res == self.S_OK

        return compound_types.PrecursorRange(
            ms_order.value,
            first_precursor_mass.value,
            last_precursor_mass.value,
            bool(valid.value)
        )

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.string_types)
    def get_scan_event_for_scan_num(self, n_scan):
        '''
        Returns scan information
        :
            GetScanEventForScanNumberTextEx(long nScan, BSTR FAR*
                pbstrScanEvent)

            -> u'FTMS + NSI !sid !cv !t !E !k !r !d !w !sa AMI !u Full !msx ms
                [400.0000-1600.0
        '''

        scan_event = comtypes.BSTR()
        res = self.msfile_lib.GetScanEventForScanNum(n_scan, scan_event)
        assert res == self.S_OK

        return scan_event.value

#    GetSegmentAndScanEventForScanNum not defined in library
#    @decorators.accepts(object, six.integer_types)
#    @decorators.returns(tuple)
#    def get_segment_and_scan_event_for_scan_num(self, n_scan):
#        '''
#        Returns the segment and event indexes
#        :
#            GetSegmentAndScanEventForScanNum(long nScanNumber, long
#                *pnSegment, long* pnScanEvent)
#        '''
#
#        segment = ctypes.c_long()
#        scan_event = ctypes.c_long()
#        res = self.msfile_lib.GetSegmentAndScanEventForScanNum(
#            n_scan,
#            segment,
#            scan_event,
#        )
#        assert res == self.S_OK
#
#        return segment.value, scan_event.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_activation_type_for_scan_num(self, n_scan):
        '''
        Returns the activation type as an integer, with the values
        enumerated in thermo_finnigan.lib_def.Activation_Type
        :
            GetActivationTypeForScanNum(long nScanNumber,
                long nMSOrder,
                long FAR *pnActivationType)
        '''

        ms_order = self.get_ms_order_for_scan_num(n_scan)
        activation_type = ctypes.c_long()
        res = self.msfile_lib.GetActivationTypeForScanNum(
            n_scan,
            ms_order,
            activation_type
        )
        assert res == self.S_OK

        return activation_type.value

#    AttributeError, no function named GetMassAnalyzerForScanNum
#    @decorators.accepts(object, six.integer_types)
#    @decorators.returns(six.integer_types)
#    def get_mass_analyzer_type_for_scan_num(self, n_scan):
#        '''
#        Returns the mass analyzer type for a given scan
#        :
#            GetMassAnalyzerForScanNum(long nScanNumber,
#                long FAR *pnMassAnalyzerType)
#        '''
#
#        analyzer_type = ctypes.c_long()
#        res = self.msfile_lib.GetMassAnalyzerForScanNum(n_scan, analyzer_type)
#        assert res == self.S_OK
#
#        return analyzer_type.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_detector_type_for_scan_num(self, n_scan):
        '''
        Returns the collision type as an integer, whose values
        are enumerated in thermo_finnigan.lib_def.Collision_Type
        :
            GetDetectorTypeForScanNum(long nScanNumber,
                long FAR *pnDetectorType)

            -> 0
        '''

        collision_type = ctypes.c_long()
        res = self.msfile_lib.GetDetectorTypeForScanNum(n_scan, collision_type)
        assert res == self.S_OK

        return collision_type.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_scan_type_for_scan_num(self, n_scan):
        '''
        Returns the scan type as an integer, whose values
        are enumerated in thermo_finnigan.lib_def.Scan_Type
        :
            GetScanTypeForScanNum(long nScanNumber,
                long FAR *pnScanType)

            -> 0
        '''

        scan_type = ctypes.c_long()
        res = self.msfile_lib.GetScanTypeForScanNum(n_scan, scan_type)
        assert res == self.S_OK

        return scan_type.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_ms_order_for_scan_num(self, n_scan):
        '''
        Returns the scan level for the scan, which are
        enumerated in thermo_finnigan.lib_def.Scan_Order
        :
            GetMSOrderForScanNum(long nScanNumber,
                long FAR *pnMassOrder)

            -> 1
        '''

        scan_order = ctypes.c_long()
        res = self.msfile_lib.GetMSOrderForScanNum(n_scan, scan_order)
        assert res == self.S_OK

        return scan_order.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(float)
    def get_precursor_mass_for_scan_num(self, n_scan):
        '''
        Returns the precursor mass from the scan
        :
            GetPrecursorMassForScanNum(long nScanNumber,
                long nMSOrder, double FAR *pdPrecursorMass)

            -> 368.52630615234375
        '''

        ms_order = self.get_ms_order_for_scan_num(n_scan)
        precursor_mass = ctypes.c_double()
        res = self.msfile_lib.GetPrecursorMassForScanNum(
            n_scan,
            ms_order,
            precursor_mass
        )
        assert res == self.S_OK

        return precursor_mass.value

    #     FOR RT

    @decorators.accepts(object, float)
    @decorators.returns(six.string_types)
    def get_filter_for_scan_rt(self, d_retention_time):
        '''
        Returns the scan filter from the nearest scan retention time
        :
            GetFilterForScanRT(double dRT, BSTR FAR* pbstrFtiler)

            -> u'FTMS + p NSI Full ms [400.0000-1600.0000]'
        '''

        scan_filter = comtypes.BSTR()
        res = self.msfile_lib.GetFilterForScanRT(d_retention_time, scan_filter)
        assert res == self.S_OK, res

        return scan_filter.value

    #    FROM SCAN

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(float)
    def rt_from_scan_num(self, n_scan):
        '''
        Returns the current retention time from the scan
        :
            RTFromScanNum(long nScanNumber, double FAR* pdRT)

            -> 0.37657
        '''

        retention_time = ctypes.c_double()
        res = self.msfile_lib.RTFromScanNum(n_scan, retention_time)
        assert res == self.S_OK, res

        return retention_time.value

    @decorators.returns(compound_types.MassList)
    def _get_mass_list(self, func, identifier, size_filter, cutoff_type,
                       cutoff_value, max_peaks, centroid, mass_range=None):
        '''
        Returns the mass lists with optional params, including
        cutoff types, centroiding flags, etc (enumerated in
        thermo_finnigan.lib_def).

        Sample scan filters can be:
            None
            ''
            'ms'
            '+ c SRM ms2 469.40@23.00[423.30-425.30]'
        :
            func(long FAR* pnScanNumber, LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)

            -> MassList(peak_width=0.0, mass_list=array([[400.24706813, ..., ],
                        [18756.12132645, ...]]), peak_flags=None, size=659)
        '''

        if isinstance(identifier, six.integer_types):
            # scan number identifier
            identifier = ctypes.c_long(identifier)
        else:
            # retention time identifier
            identifier = ctypes.c_double(identifier)
        peak_width = ctypes.c_double(0)
        mass_list = comtypes.automation.VARIANT()
        peak_flags = comtypes.automation.VARIANT()
        size = ctypes.c_long()

        if mass_range is None:
            res = func(
                identifier,
                size_filter,
                cutoff_type,
                cutoff_value,
                max_peaks,
                centroid,
                peak_width,
                mass_list,
                peak_flags,
                size
            )
        else:
            res = func(
                identifier,
                size_filter,
                cutoff_type,
                cutoff_value,
                max_peaks,
                centroid,
                peak_width,
                mass_list,
                peak_flags,
                mass_range,
                size
            )
        assert res == self.S_OK

        with comtypes.safearray.safearray_as_ndarray:
            return compound_types.MassList(
                peak_width.value,
                mass_list.value,
                peak_flags.value,
                size.value
            )

    def get_mass_list_from_scan_num(self, *args):
        '''
        Returns the masslists for the current scan
        :
            GetMassListFromScanNum(long FAR* pnScanNumber, LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)

            -> MassList(peak_width=0.0, mass_list=array([[400.24706813, ..., ],
                        [18756.12132645, ...]]), peak_flags=None, size=659)
        '''

        assert len(args) == 6
        func = self.msfile_lib.GetMassListFromScanNum
        return self._get_mass_list(func, *args)

    def get_next_mass_list_from_scan_num(self, *args):
        '''
        Returns masslists for the next applicable scan, after filtering,
        relative to the current scan
        :
            GetNextMassListFromScanNum(long FAR* pnScanNumber,
                LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)
        '''

        assert len(args) == 6
        func = self.msfile_lib.GetNextMassListFromScanNum
        return self._get_mass_list(func, *args)

    def get_prev_mass_list_from_scan_num(self, *args):
        '''
        Returns masslists for the previous applicable scan, after filtering,
        relative to the current scan
        :
            GetPrevMassListFromScanNum(long FAR* pnScanNumber,
                LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)
        '''

        assert len(args) == 6
        func = self.msfile_lib.GetPrevMassListFromScanNum
        return self._get_mass_list(func, *args)

    def get_mass_list_range_from_scan_num(self, *args):
        '''
        Returns the closest matching scan to n_scan
        :
            GetMassListRangeFromScanNum(long* pnScanNumber, BSTR
                bstrFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                double* pdCentroidPeakWidth,
                VARIANT* pvarMassList,
                VARIANT* pvarPeakFlags,
                LPCTSTR csMassRange1,
                long* pnArraySize)
        '''

        assert len(args) == 7
        func = self.msfile_lib.GetMassListRangeFromScanNum
        return self._get_mass_list(func, *args)

    def get_next_mass_list_range_from_scan_num(self, *args):
        '''
        Returns the closest matching scan after n_scan
        :
            GetNextMassListRangeFromScanNum(long FAR* pnScanNumber,
                LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                LPCTSTR szMassRange1,
                long FAR* pnArraySize)
        '''

        assert len(args) == 7
        func = self.msfile_lib.GetNextMassListRangeFromScanNum
        return self._get_mass_list(func, *args)

#    BROKEN
#    def get_precursor_info_from_scan_num(self, n_scan):
#        '''GetPrecursorInfoFromScanNum'''

    def get_prev_mass_list_range_from_scan_num(self, *args):
        '''
        Returns the closest matching scan after n_scan
        :
            GetPrevMassListRangeFromScanNum(long FAR* pnScanNumber,
                LPCTSTR szFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks,
                BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                LPCTSTR szMassRange1,
                long FAR* pnArraySize)
        '''

        assert len(args) == 7
        func = self.msfile_lib.GetPrevMassListRangeFromScanNum
        return self._get_mass_list(func, *args)

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_msx_multiplex_value_from_scan_num(self, n_scan):
        '''
        Returns the multiplx mode, which is enumerated in
        thermo_finnigan.lib_def.Multiplex_Type
        :
            GetMSXMultiplexValueFromScanNum(long nScanNumber, long *pnMSXValue)

            -> 1
        '''

        msx = ctypes.c_long()
        res = self.msfile_lib.GetMSXMultiplexValueFromScanNum(n_scan, msx)
        assert res == self.S_OK, res

        return msx.value

    @decorators.accepts(object, six.integer_types, six.integer_types)
    @decorators.returns(float)
    def get_mass_calibration_from_scan_num(self, n_scan, n_calibration_index):
        '''
        Returns the mass calibration data from a scan
        :
            GetMassCalibrationValueFromScanNum(long nScanNumber, long
                nMassCalibrationIndex, double *pdMassCalibrationValue)

            -> 0.0
        '''

        mass_calibration = ctypes.c_double()
        res = self.msfile_lib.GetMassCalibrationValueFromScanNum(
            n_scan,
            n_calibration_index,
            mass_calibration
        )
        assert res == self.S_OK, res

        return mass_calibration.value

#    Broken
#    def get_full_ms_order_precursor_data_from_scan_num(self, n_scan):
#        '''
#        Returns the full precursor data for
#        :
#            GetFullMSOrderPrecursorDataFromScanNum(long nScanNumber, long
#                nMSOrder, LPVARIANT pvarFullMSOrderPrecursorInfo)
#        '''
#
#        ms_order = self.get_ms_order_for_scan_num(n_scan)
#        precursor_info = comtypes.automation.VARIANT()

    @decorators.accepts(object, six.integer_types, six.integer_types)
    @decorators.returns(compound_types.MassRange)
    def get_mass_range_from_scan_num(self, n_scan, n_range_index):
        '''
        Returns the high and low mass information from a scan
        :
            GetMassRangeFromScanNum(long nScanNumber, long nMassRangeIndex,
                double *pdMassRangeLowValue, double *pdMassRangeHighValue)

            -> MassRange(low=400.0, high=1600.0)
        '''

        low_mass = ctypes.c_double()
        high_mass = ctypes.c_double()

        res = self.msfile_lib.GetMassRangeFromScanNum(
            n_scan,
            n_range_index,
            low_mass,
            high_mass
        )
        assert res == self.S_OK, res

        return compound_types.MassRange(low_mass.value, high_mass.value)

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.string_types)
    def get_compound_name_from_scan_num(self, n_scan):
        '''
        Returns a compound name for the scan
        :
            GetCompoundNameFromScanNum(int nScanNumber , BSTR *pbstrCompoundName)

            -> ''
        '''

        compound_name = comtypes.BSTR()
        res = self.msfile_lib.GetCompoundNameFromScanNum(n_scan, compound_name)
        assert res == self.S_OK, res

        return compound_name.value

    @decorators.accepts(object, six.integer_types, six.string_types)
    @decorators.returns(six.integer_types)
    def _get_x_value_from_scan_num(self, n_scan, parameter):
        '''
        Returns a parameter {'A', 'B', 'F', 'K', 'R', 'V'} from
        the scan number.
        :
            GetXValueFromScanNum(long nScanNumber, long *pnXValue)

            -> 2
        '''

        parameter_value = ctypes.c_long()
        name = "Get{}ValueFromScanNum".format(parameter)
        fun = getattr(self.msfile_lib, name)
        res = fun(n_scan, parameter_value)
        assert res == self.S_OK, res

        return parameter_value.value

    def get_a_value_from_scan_num(self, n_scan):
        '''Returns the A value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'A')

    def get_b_value_from_scan_num(self, n_scan):
        '''Returns the B value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'B')

    def get_f_value_from_scan_num(self, n_scan):
        '''Returns the F value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'F')

    def get_k_value_from_scan_num(self, n_scan):
        '''Returns the K value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'K')

    def get_r_value_from_scan_num(self, n_scan):
        '''Returns the R value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'R')

    def get_v_value_from_scan_num(self, n_scan):
        '''Returns the V value from the scan number'''

        return self._get_x_value_from_scan_num(n_scan, 'V')

    def get_segmented_mass_list_from_scan_num(self,
        n_scan, size_filter, cutoff_type,
        cutoff_value, max_peaks, centroid):
        '''
        Returns the segmented mass list closest the the scan number
        :
             GetSegmentMassListFromScanNum(long *pnScanNumber, BSTR bstrFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks, BOOL bCentroidResult,
                double *pdCentroidPeakWidth,
                VARIANT * pvarMassList, VARIANT * pvarPeakFlags,
                long *pnArraySize, VARIANT *pvarSegments,
                long *pnNumSegments,
                VARIANT *pvarMassRange)

            -> -> SegmentedMassList(
                peak_width=0.0, mass_list=array([[400.24706813, ..., ],
                [18756.12132645, ...]]), peak_flags=None, size=659,
                segments=([659]), segment_count=1,
                mass_range=MassRange(low=400.0, high=1600.0))
        '''

        scan = ctypes.c_long(n_scan)
        peak_width = ctypes.c_double(0)
        mass_list = comtypes.automation.VARIANT()
        peak_flags = comtypes.automation.VARIANT()
        size = ctypes.c_long()
        segments = comtypes.automation.VARIANT()
        number_segments = ctypes.c_long()
        mass_range = comtypes.automation.VARIANT()

        res = self.msfile_lib.GetSegmentedMassListFromScanNum(
            scan,
            size_filter,
            cutoff_type,
            cutoff_value,
            max_peaks,
            centroid,
            peak_width,
            mass_list,
            peak_flags,
            size,
            segments,
            number_segments,
            mass_range
        )
        assert res == self.S_OK

        low_mass = mass_range.value[0][0]
        high_mass = mass_range.value[1][0]
        mass_range = compound_types.MassRange(low_mass, high_mass)
        with comtypes.safearray.safearray_as_ndarray:
            return compound_types.SegmentedMassList(
                peak_width.value,
                mass_list.value,
                peak_flags.value,
                size.value,
                segments.value,
                number_segments.value,
                mass_range
            )

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_mass_ranges_from_scan_num(self, n_scan):
        '''
        Returns the numeric identifier for the mass range data
        :
            GetNumberOfMassRangesFromScanNum(int nScanNumber, long
                *pnNumMassRanges)

            -> 1
        '''

        mass_ranges = ctypes.c_long()
        res = self.msfile_lib.GetNumberOfMassRangesFromScanNum(
            n_scan,
            mass_ranges
        )
        assert res == self.S_OK, res

        return mass_ranges.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_ms_orders_from_scan_num(self, n_scan):
        '''
        Returns the number of MS reactions (collisions) for the scan
        :
            GetNumberOfMSOrdersFromScanNum(long nScanNumber, long *pnNumMSOrders)

            -> 1
        '''

        ms_orders = ctypes.c_long()
        res = self.msfile_lib.GetNumberOfMSOrdersFromScanNum(
            n_scan,
            ms_orders
        )
        assert res == self.S_OK, res

        return ms_orders.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_mass_calibrators_from_scan_num(self, n_scan):
        '''
        Returns the number of MS reactions (collisions) for the scan
        :
            GetNumberOfMassCalibratorsFromScanNum(int nScanNumber, long
                *pnNumMassCalibrators)

            -> 7
        '''

        calibrators = ctypes.c_long()
        res = self.msfile_lib.GetNumberOfMassCalibratorsFromScanNum(
            n_scan,
            calibrators
        )
        assert res == self.S_OK, res

        return calibrators.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_cycle_number_from_scan_num(self, n_scan):
        '''
        Returns the cycle number from the scan index
        :
            GetCycleNumberFromScanNumber(long nScanNumber, long *pnCycleNumber)

            -> 0
        '''

        cycle_number = ctypes.c_long()
        res = self.msfile_lib.GetCycleNumberFromScanNumber(
            n_scan,
            cycle_number
        )
        assert res == self.S_OK, res

        return cycle_number.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_source_fragments_from_scan_num(self, n_scan):
        '''
        Returns the source fragments in the scan
        :
             GetNumberOfSourceFragmentsFromScanNum(long nScanNumber, long
                *pnNumSourceFragments)

            -> 0
        '''

        source_fragments = ctypes.c_long()
        res = self.msfile_lib.GetCycleNumberFromScanNumber(
            n_scan,
            source_fragments
        )
        assert res == self.S_OK, res

        return source_fragments.value

    @decorators.accepts(object, six.integer_types, six.integer_types)
    @decorators.returns(float)
    def get_source_fragments_value_from_scan_num(self, n_scan,
                                                 n_fragment_index):
        '''
        Returns the value of the source fragments from a given index,
        in the range of the number of source fragments
        :
             GetSourceFragmentValueFromScanNum(long nScanNumber, long
                nSourceFragmentIndex, double *pdSourceFragmentValue)

            -> 6.443e-321 (seems to be wrong bit order)
        '''

        fragment_value = ctypes.c_double()
        res = self.msfile_lib.GetSourceFragmentValueFromScanNum(
            n_scan,
            n_fragment_index,
            fragment_value
        )
        assert res == self.S_OK, res

        return fragment_value.value

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(six.integer_types)
    def get_number_of_source_fragmentation_mass_ranges_from_scan_num(
        self, n_scan):
        '''
        Returns the number of fragmentation mass ranges
        :
             GetNumberOfSourceFragmentationMassRangesFromScanNum(long
                nScanNumber, long *pnNumSourceFragmentationMassRanges)

            -> 0
        '''

        mass_ranges = ctypes.c_long()
        lib = self.msfile_lib
        res = lib.GetNumberOfSourceFragmentationMassRangesFromScanNum(
            n_scan,
            mass_ranges
        )
        assert res == self.S_OK, res

        return mass_ranges.value

    @decorators.accepts(object, six.integer_types, six.integer_types)
    @decorators.returns(compound_types.MassRange)
    def get_source_fragmentation_mass_range_from_scan_num(
        self, n_scan, n_fragment_index):
        '''
        Returns the the fragmentation mass range from the scan and index,
        in the range of the number of fragmentation mass ranges.
        :
            GetSourceFragmentationMassRangeFromScanNum(long nScanNumber, long
                nSourceFragmentIndex, double *pdSourceFragmentRangeLowValue,
                double *pdSourceFragmentRangeHighValue)

            -> MassRange(low=50.0, high=2000.0)
        '''

        low_mass = ctypes.c_double()
        high_mass = ctypes.c_double()
        res = self.msfile_lib.GetSourceFragmentationMassRangeFromScanNum(
            n_scan,
            n_fragment_index,
            low_mass,
            high_mass
        )
        assert res == self.S_OK, res

        return compound_types.MassRange(low_mass.value, high_mass.value)

    #     FROM RT

    def get_mass_list_from_rt(self, *args):
        '''
        Returns masslists for the nearest scan to the RT
        :
            GetMassListFromRT(double FAR* pdRT, LPCTSTR szFilter,
                long nIntensityCutoffType, long nIntensityCutoffValue,
                long nMaxNumberOfPeaks, BOOL bCentroidResult,
                VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                long FAR* pnArraySize)
        '''

        assert len(args) == 6
        func = self.msfile_lib.GetMassListFromRT
        return self._get_mass_list(func, *args)

    def get_mass_list_range_from_rt(self, *args):
        '''
        Returns masslist range closest to the RT
        :
            GetMassListRangeFromRT(double FAR* pdRT, LPCTSTR szFilter,
                long nIntensityCutoffType, long
                nIntensityCutoffValue,
                long nMaxNumberOfPeaks, BOOL
                bCentroidResult, VARIANT FAR* pvarMassList,
                VARIANT FAR* pvarPeakFlags,
                LPCTSTR szMassRange1,
                long FAR* pnArraySize)
        '''

        assert len(args) == 7
        func = self.msfile_lib.GetMassListRangeFromRT
        return self._get_mass_list(func, *args)

    @decorators.accepts(object, float)
    @decorators.returns(six.integer_types)
    def scan_num_from_rt(self, d_retention_time):
        '''
        Returns the scan number closest to the retention time
        :
            ScanNumFromRT(double dRT, long FAR* pnScanNumber)

            -> 368
        '''

        scan = ctypes.c_long()
        res = self.msfile_lib.ScanNumFromRT(d_retention_time, scan)
        assert res == self.S_OK, res

        return scan.value

    def get_segmented_mass_list_from_rt(self,
        d_retention_time, size_filter, cutoff_type,
        cutoff_value, max_peaks, centroid):
        '''
        Returns the segmented mass list closest the the scan number
        :
             GetSegmentedMassListFromRT(double *pdRT, BSTR bstrFilter,
                long nIntensityCutoffType,
                long nIntensityCutoffValue,
                long nMaxNumberOfPeaks, BOOL bCentroidResult,
                double *pdCentroidPeakWidth,
                VARIANT * pvarMassList, VARIANT * pvarPeakFlags,
                long *pnArraySize, VARIANT *pvarSegments,
                long *pnNumSegments,
                VARIANT *pvarLowHighMassRange)

            -> -> SegmentedMassList(
                peak_width=0.0, mass_list=array([[400.24706813, ..., ],
                [18756.12132645, ...]]), peak_flags=None, size=659,
                segments=([659]), segment_count=1,
                mass_range=MassRange(low=400.0, high=1600.0))
        '''

        retention_time = ctypes.c_double(d_retention_time)
        peak_width = ctypes.c_double(0)
        mass_list = comtypes.automation.VARIANT()
        peak_flags = comtypes.automation.VARIANT()
        size = ctypes.c_long()
        segments = comtypes.automation.VARIANT()
        number_segments = ctypes.c_long()
        mass_range = comtypes.automation.VARIANT()

        res = self.msfile_lib.GetSegmentedMassListFromRT(
            retention_time,
            size_filter,
            cutoff_type,
            cutoff_value,
            max_peaks,
            centroid,
            peak_width,
            mass_list,
            peak_flags,
            size,
            segments,
            number_segments,
            mass_range
        )
        assert res == self.S_OK

        low_mass = mass_range.value[0][0]
        high_mass = mass_range.value[1][0]
        mass_range = compound_types.MassRange(low_mass, high_mass)
        with comtypes.safearray.safearray_as_ndarray:
            return compound_types.SegmentedMassList(
                peak_width.value,
                mass_list.value,
                peak_flags.value,
                size.value,
                segments.value,
                number_segments.value,
                mass_range
            )

    #    DATA

    @decorators.accepts(object, six.integer_types)
    @decorators.returns(tuple)
    def get_all_ms_order_data(self, n_scan):
        '''
        Returns all ms order data from the scan event.
        :
             GetAllMSOrderData(long nScanNumber, VARIANT FAR* pvarDoubleData,
                VARIANT FAR* pvarFlagsData, long FAR* pnNumberOfMSOrders )
        '''

        double_data = comtypes.automation.VARIANT()
        flags_data = comtypes.automation.VARIANT()
        ms_orders = ctypes.c_long()
        res = self.msfile_lib.GetAllMSOrderData(
            n_scan,
            double_data,
            flags_data,
            ms_orders
        )
        assert res == self.S_OK

        with comtypes.safearray.safearray_as_ndarray:
            collated = zip(*double_data.value)
            double_data = [compound_types.MSOrderData(*i) for i in collated]
            return double_data, flags_data.value, ms_orders.value

    @decorators.accepts(object)
    @decorators.returns(bool)
    def is_there_ms_data(self):
        '''
        Returns if any MS data found in the raw file.
        :
            IsThereMSData(BOOL FAR* pbMSData)

            -> False
        '''

        ms_data = ctypes.c_long()
        res = self.msfile_lib.IsThereMSData(ms_data)
        assert res == self.S_OK, res

        return bool(ms_data.value)

    #    AGGREGATE

    # GetAverageMassList
    # This is probably what Skyline uses...
    # GetAveragedMassSpectrum
    # GetSummedMassSpectrum
    # GetLabelData
    # GetAveragedLabelData
    # GetNoiseData

    #     TRAILER

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_num_trailer_extra(self):
        '''
        Returns the extra values recorded by the controller.
        :
            GetNumTrailerExtra(long FAR* pnNumberOfTrailerExtraEntries)
        '''

        extra = ctypes.c_long()
        res = self.msfile_lib.GetNumTrailerExtra(extra)
        assert res == self.S_OK, res

        return extra.value

    # GetTrailerExtraForScanNum
    # GetTrailerExtraLabelsForScanNum
    # GetTrailerExtraValueForScanNum
    # GetTrailerExtraLabelsForRT
    # GetTrailerExtraForRT
    # GetTrailerExtraValueForRT

    #   TUNE DATA

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_num_tune_data(self):
        '''
        Returns the total number of TUNE data entries acquired by the
        controller.
        :
             GetNumTuneData(long FAR* pnNumTuneData)
        '''

        tune_data = ctypes.c_long()
        res = self.msfile_lib.GetNumTuneData(tune_data)
        assert res == self.S_OK, res

        return tune_data.value

    # GetTuneData
    # GetTuneDataValue
    # GetTuneDataLabels

    #     LOGS

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_num_status_log(self):
        '''
        Returns the total number of log entries acquired by the controller.
        :
             GetNumStatusLog(long FAR* pnNumberOfStatusLogEntries)
        '''

        status_logs = ctypes.c_long()
        res = self.msfile_lib.GetNumStatusLog(status_logs)
        assert res == self.S_OK, res

        return status_logs.value

    @decorators.accepts(object)
    @decorators.returns(six.integer_types)
    def get_num_error_log(self):
        '''
        Returns the total number of log entries acquired by the controller.
        :
             GetNumErrorLog(long FAR* pnNumberOfErrorLogEntries)
        '''

        error_logs = ctypes.c_long()
        res = self.msfile_lib.GetNumErrorLog(error_logs)
        assert res == self.S_OK, res

        return error_logs.value

    # GetStatusLogLabelsForScanNum
    # GetStatusLogValueForScanNum
    # GetErrorLogItem
    # GetStatusLogForPos
    # GetStatusLogPlottableIndex
    # GetStatusLogForScanNum
    # GetStatusLogLabelsForRT
    # GetStatusLogForRT
    # GetStatusLogValueForRT

    #    METHODS

    # GetNumInstMethods
    # HasExpMethod
    # GetInstMethod
    # ExtractInstMethodFromRaw
    # GetInstMethodNames

    # VERSION/HARDWARE

    # GetInstName
    # GetInstModel
    # GetInstSerialNumber
    # IsQExactive
    # GetInstSoftwareVersion
    # GetInstHardwareVersion
    # Version

    #   PARAMETERS

    # GetInstrumentID
    # GetInletID
    # GetErrorFlag
    # GetSampleVolume
    # GetSampleWeight
    # GetVialNumber
    # GetInjectionVolume
    # GetFlags
    # GetAcquisitionFileName
    # GetInstrumentDescription
    # GetAcquisitionDate
    # GetOperator
    # GetComment1
    # GetComment2
    # GetSampleAmountUnits
    # GetInjectionAmountUnits
    # GetSampleVolumeUnits
    # GetInstFlags
    # GetInstNumChannelLabels
    # GetInstChannelLabel
    # GetFilters
    # GetUniqueCompoundNames
    # GetMassTolerance

    # GetFilterMassPrecision

    #   SET DATA

    # SetMassTolerance

    #   CHROMATOGRAMS

    # GetChroData
    # GetChros
    # GetChroByCompoundName
