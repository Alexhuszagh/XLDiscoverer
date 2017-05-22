'''
    Resources/Chemical_Defs/reporterions
    ____________________________________

    Stores report ion definitions for product ion-level quantitation.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from namedlist import namedlist

from xldlib.general import sequence
from xldlib.utils import serialization

from . import dicttools
from .. import paths
from ..parameters import defaults


# PATHS
# -----
REPORTERION_PATH = os.path.join(paths.DIRS['data'], 'reporterions.json')


# OBJECTS
# -------


@sequence.serializable("ReporterIonFragment")
class Fragment(namedlist("Fragment", [
    'name',
    'formula',
    'charge',
    ('active', False)
])):
    '''Reporter ion configuration definitions'''


@sequence.serializable("ReporterIon")
class ReporterIon(namedlist("ReporterIon", "id name modification fragments")):
    '''Definitions for a report ion set'''


@serialization.register("StoredReporterIons")
class StoredReporterIons(dicttools.StoredNames):
    '''Stores crosslinkers with sequential primary keys'''

    reporterion_error = "Reporter Ion not recognized"

    #      I/O

    def loader(self):
        '''Loads from a target configuration file'''

        document = self._ioload()
        if document is not None:
            keys = sorted(document, key=int)

            for key in keys:
                reporterion = ReporterIon(*document[key])
                fragments = [Fragment(*i) for i in reporterion.fragments]
                reporterion = reporterion._replace(fragments=fragments)

                self[int(key)] = crosslinker

    #    PUBLIC

    @property
    def current(self):
        return self[defaults.DEFAULTS['current_reporterions']]

    @current.setter
    def current(self, value):
        self[defaults.DEFAULTS['current_reporterions']] = value

    #    HELPERS

    def _valuechecker(self, reporterion):
        '''Checks whether a reporterion object or a possible object'''

        if isinstance(reporterion, ReporterIon):
            return reporterion

        elif isinstance(reporterion, tuple) and len(reporterion) == 2:
            return ReporterIon(self._get_new_key(), *reporterion)

        else:
            raise AssertionError(self.reporterion_error)


# DATA
# ----

REPORTER_IONS = StoredReporterIons(REPORTERION_PATH, [
    (1, ReporterIon(id=1,
        name='TMT2plex',
        modification=203,
        fragments=[
            Fragment(name='TMT-126',
                formula='C8 N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-127',
                formula='C8 15N H15',
                charge=1,
                active=True)
        ])),
    (2, ReporterIon(id=2,
        name='TMT6plex',
        modification=206,
        fragments=[
            Fragment(name='TMT-126',
                formula='C8 N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-127',
                formula='C8 15N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-128',
                formula='C6 13C2 N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-129',
                formula='C6 13C2 15N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-130',
                formula='C4 13C4 N H15',
                charge=1,
                active=True),
            Fragment(name='TMT-131',
                formula='C4 13C4 15N H15',
                charge=1,
                active=True)
        ]))
])
