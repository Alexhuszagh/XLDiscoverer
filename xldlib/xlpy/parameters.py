'''
    XlPy/parameters
    _______________

    Runtime parameters for main thread, which can be partially
    reconstructed from the run dataset.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib import exception
from xldlib.objects import chemical
from xldlib.qt.objects import base
from xldlib.resources import chemical_defs, engines
from xldlib.utils import logger

from . import wrappers

# DATA
# ----

FIELDS = (
    'modifications',
    'crosslinkers',
    'fragments',
    'isobaric',
    'search',
    'spectra',
    'profiles',
    'profile',
    'reporterion'
)


# PARAMETERS
# ----------


@logger.init('xlpy', 'DEBUG')
class Parameters(base.BaseObject):
    '''Stores parameters during runtime'''

    # SETTINGS
    # --------
    _fields = FIELDS

    def __init__(self, **kwds):
        super(Parameters, self).__init__()

        self.setmodifications(kwds.get('modifications'))
        self.setcrosslinkers(kwds.get('crosslinkers'), kwds.get('fragments'))
        self.setsearchengines(kwds.get('search'))
        self.setspectralformats(kwds.get('spectra'))
        self.setprofiles(kwds.get('profiles'), kwds.get('profile'))
        self.setreporterion(kwds.get('reporterion'))

    @classmethod
    def frommatched(cls, matched):
        import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()

    #     SETTERS

    def setmodifications(self, modifications=None):
        if modifications is None:
            modifications = chemical_defs.MODIFICATIONS
        self.modifications = modifications

    def setcrosslinkers(self, crosslinkers=None, fragments=None):
        '''Identifies and sets the current crosslinker selection'''

        if crosslinkers is None:
            crosslinkers = chemical_defs.CROSSLINKERS
            self.crosslinkers = crosslinkers.todict()
            self.fragments = crosslinkers.fragmentstodict(self.modifications)
        else:
            self.crosslinkers = crosslinkers
            self.fragments = fragments
        self.isobaric = chemical.Isobaric.new(self.crosslinkers,
                                              self.modifications)

    def setsearchengines(self, search=None):
        '''Sets the search engines for the matched search'''

        if search is None:
            search = engines.SEARCH
            search.setmodifications()
        self.search = search

    def setspectralformats(self, spectra=None):
        '''Sets the spectral formats for the raw files'''

        if spectra is None:
            spectra = engines.SPECTRA
        self.spectra = spectra

    def setprofiles(self, profiles=None, profile=None):
        '''Sets the current profiles and currently selected profile'''

        if profiles is None:
            profiles = chemical_defs.PROFILES
        self.profiles = profiles

        if profile is None:
            profile = profiles.current
        self.profile = profile

    def setreporterion(self, reporterion=None):
        '''Sets the reporter ion object for the quantitation'''

        # TODO: can fix a lot of stuff here...
        if reporterion is None:
            reporterion = chemical_defs.REPORTER_IONS.current
        self.reporterion = reporterion

    #     HELPERS

    def items(self):
        for key in FIELDS:
            yield key, getattr(self, key)

    @wrappers.threadstop(AssertionError, exception.CODES['012'])
    def checkcrosslinkers(self):
        assert self.crosslinkers

    @wrappers.threadstop(AssertionError, exception.CODES['020'])
    def checkprofile(self):
        '''Checks if the profile matches the crosslinker selection'''

        crosslinkers = tuple(sorted(self.crosslinkers))
        profiles = self.profiles[crosslinkers]

        assert self.profile.id in profiles
