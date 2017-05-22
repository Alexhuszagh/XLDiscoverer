'''
    Resources/Other/spectra
    _______________________

    Definitions for various spectral formats, such as DTA, MGF, mzXML,
    mzML, etc.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import tables as tb

from namedlist import namedlist

from xldlib.definitions import re
from xldlib.general import sequence
from xldlib.utils import serialization
from xldlib.utils.io_ import typechecker

from . import dicttools

# ENUMS
# -----

IDENTIFIERS = tb.Enum([
    'mgf',
    'mzxml',
    'mzml'
])

SPECTRAL_FORMATS = tb.Enum([
    'RAW',
    'HDF5',
    'XML',
    'TEXT'
])

# OBJECTS
# -------


@sequence.serializable("SpectralFormatVersion")
class Version(namedlist("Version", "name major minor revision "
    "distiller format defaults")):

    #     PUBLIC

    def tostr(self):
        '''String representation of the version'''

        return "{0}.{1}.{2}, {3}".format(self.major, self.minor,
            self.revision, self.distiller)


MgfDefaults = namedlist("MgfDefaults", "regexp start end skip")
MzmlDefaults = namedlist("MzmlDefaults", "regexp")
MzxmlDefaults = namedlist("MzxmlDefaults", "regexp")
LinkDefaults = namedlist("LinkDefaults", "regexp")


@serialization.register("SpectralFormat")
class SpectralFormat(dicttools.EngineDict):
    '''Method definitions for spectral format objects'''

    #     PUBLIC

    def matchfile(self, fileobj):
        '''Matches a given fileobj to a spectral database format'''

        fileformat = _fileformat(fileobj)
        return getattr(self, '_match' + fileformat.lower())(fileobj)

    #    NON-PUBLIC

    @dicttools.read_header
    def _matchxml(self, header, error=None):
        '''Returns the file format for a spectra XML file'''

        for name, version, engine in self.iterengines('XML'):
            if re.match(engine.defaults.regexp, header):
                return name, version, error

    @dicttools.read_header
    def _matchtext(self, header, error=None):
        '''Returns the file format for a spectra text file'''

        for name, version, engine in self.iterengines('TEXT'):
            regex = engine.defaults.regexp
            if re.match(regex, header):
                return name, version, error


# PRIVATE
# -------


def _fileformat(fileobj):
    '''
    Call file type-checkers to determine the type of
    file. A header, typically under 100 bytes, is read from the
    file and matched to a known filetype. If the file has a known
    format, return that format, Otherwise, if no encoding/decoding
    error is raised, return 'TEXT'.
    '''

    if typechecker.raw(fileobj):
        return 'RAW'
    elif typechecker.hdf5(fileobj.name):
        return 'HDF5'
    elif typechecker.xml(fileobj):
        return 'XML'
    else:
        return 'TEXT'


# DATA
# ----

SPECTRA = SpectralFormat({
    'mgf': {
        'None.None.None, MS Convert': Version('mgf', None, None, None,
            distiller="MS Convert",
            format='TEXT',
            defaults=MgfDefaults(
                regexp=(r'BEGIN IONS\r?\n'
                        r'TITLE=(.*)\.[0-9]+\.[0-9]+\.[0-9]* '
                        # one massively long line
                        r'File:\"(.*)\", NativeID:\"'
                        r'controllerType=[0-9]+ controllerNumber=[0-9]+ '
                        r'scan=(?P<num>[0-9]+)\"\r?\n'
                        # newline
                        r'RTINSECONDS=([0-9]*\.?[0-9]*)\r?\n'
                        r'PEPMASS=([0-9]+\.[0-9]+)'
                        r'(?: ([0-9]*\.[0-9]+))?\r?\n'
                        r'(CHARGE=([0-9]+)\+\r?\n)?'),
                start='BEGIN IONS',
                end='END IONS',
                skip=0)),
        'None.None.None, PAVA': Version('mgf', None, None, None,
            distiller="PAVA",
            format='TEXT',
            defaults=MgfDefaults(
                regexp=(r'^BEGIN IONS\r?\n'
                        # In case of file header line, in _ms3cid files
                        r'(.*\r?\n)?'
                        # precursor at MS2 scan level
                        r'(?:MS2_SCAN_NUMBER= ([0-9]+)\r?\n)?'
                        r'TITLE=Scan ([0-9]+) '
                        r'\(rt=([0-9]*\.[0-9]+)\) \[(.*)\]\r?\n'
                        r'PEPMASS=([0-9]+\.?[0-9]*)\s+'
                        r'([0-9]*(\.?[0-9]*)?)\r?\n'
                        # Line could be missing if CHARGE=1+
                        r'(CHARGE=([0-9]+)\+\r?\n)?'),
                start='BEGIN IONS',
                end='END IONS',
                skip=0)),
        'None.None.None, ProteoWizard': Version('mgf', None, None, None,
            distiller="ProteoWizard",
            format='TEXT',
            defaults=MgfDefaults(
                regexp=(r'(?:MASS=Monoisotopic\r?\n)?'
                        r'BEGIN IONS\r?\n'
                        r'TITLE=(.*) Spectrum([0-9]+) scans: ([0-9]+)\r?\n'
                        r'PEPMASS=([0-9]+\.[0-9]+) ([0-9]*\.?[0-9]*)\r?\n'
                        r'(?:CHARGE=([0-9]+)\+\r?\n)?'
                        r'RTINSECONDS=([0-9]+)\r?\n'
                        r'SCANS=([0-9]+)\r?\n'),
                start='BEGIN IONS',
                end='END IONS',
                skip=1)),
        'None.None.None, Pava FullMs': Version('mgf', None, None, None,
            distiller="Pava FullMs",
            format='TEXT',
            defaults=MgfDefaults(
                regexp=(r'Scan#: ([0-9]+)\r?\n'
                        r'Ret\.Time: ([0-9]*\.?[0-9]*)\r?\n'
                        r'IonInjectionTime\(ms\): ([0-9]*\.?[0-9]*)\r?\n'
                        r'TotalIonCurrent: ([0-9]*\.?[0-9]*)\r?\n'
                        r'BasePeakMass: ([0-9]+\.?[0-9]*)\r?\n'
                        r'BasePeakIntensity: ([0-9]*\.?[0-9]*)\r?\n'),
                start="Scan#:",
                end=r'\r?\n\r?\n\r?\n',
                skip=0)),
    },
    'mzml': {
        '3.65.0, MSConvert': Version('mzml', 3, 65, 0,
            distiller="MSConvert",
            format='XML',
            defaults=MzmlDefaults(
                regexp=(r'^<\?xml version="1.0" '
                        r'encoding="(.*)"\?>\r?\n<indexedmzML '
                        r'xmlns="(.*)" xmlns:xsi="(.*)" '
                        r'xsi:schemaLocation="(.*) (.*)">\r?\n'
                        r'  <mzML xmlns="(.*)" xmlns:xsi="(.*)"'
                        r' xsi:schemaLocation="(.*) (.*)" id="(.*)"'
                        r' version="(.*)">')))
    },
    'mzxml': {
        '3.2.0, MSConvert': Version('mzxml', 3, 2, 0,
            distiller="MSConvert",
            format='XML',
            defaults=MzxmlDefaults(
                regexp=(r'^<\?xml version="1.0" '
                        r'encoding="(.*)"\?>\r?\n<mzXML xmlns="(.*)"\r?\n'
                        r'       xmlns:xsi="(.*)"\r?\n       xsi:'
                        r'schemaLocation="(.*) (.*)">\r?\n  ')))
    },
    'link': {
        'None.None.None, PAVA': Version('link', None, None, None,
            distiller="PAVA",
            format='TEXT',
            defaults=LinkDefaults(
                regexp=r'^ms3_sn\tms3_rt\tms2_sn\tms2_rt\r?\n'))
    }
})
