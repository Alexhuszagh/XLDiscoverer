'''
    XlPy/ProductQuantitation/core
    _____________________________

    Core module for calculating product-level report ion ratios.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# losd modules
import operator as op

import numpy as np

from collections import namedtuple

from xldlib import chemical
from xldlib.definitions import partial, ZIP
from xldlib.general import sequence
from xldlib.onstart.main import APP
from xldlib.resources import chemical_defs
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, masstools
from xldlib.xlpy import wrappers


# OBJECTS
# -------


class ReporterIon(namedtuple("ReporterIon", "name mz")):
    '''Definitions for a reporter ion query'''

    #  CLASS METHODS

    @classmethod
    def fromfragment(cls, fragment):
        '''Initializes a reporter ion from a Fragment instance'''

        mass = chemical.Molecule(fragment.formula).mass
        mz = masstools.mz(mass, fragment.charge)
        return cls(fragment.name, mz)


class MassWindow(namedtuple("MassWindow", "min max")):
    '''Definitions for a mass window object'''

    #  CLASS METHODS

    @classmethod
    def fromfragments(cls, fragments, padding=10):
        '''Initializes the class from a list of fragments'''

        return cls(
            min(i.mz for i in fragments) - padding,
            max(i.mz for i in fragments) + padding)


class IonQuery(namedtuple("IonQuery", "ions fragments window mzs")):
    '''Definitions for an reporter ion m/zs to extract'''

    #  CLASS METHODS

    @classmethod
    def new(cls):
        '''Initializes a new IonQuery object from the current profile'''

        # TODO: this should be defined in resources and encapsulated
        ions = chemical_defs.REPORTER_IONS.current
        active = (i for i in ions.fragments if i.active)
        fragments = [ReporterIon.fromfragment(i) for i in active]
        window = MassWindow.fromfragments(fragments)
        mzs = np.array([i.mz for i in fragments]).reshape((-1, 1))

        return cls(ions, fragments, window, mzs)

    #     PUBLIC

    def where(self, mz):
        '''Indexes where the error from target to query is less than PPM'''

        diff = abs(mz - self.mzs)
        if defaults.DEFAULTS['reporterion_error_mode'] == 'PPM':
            ppm = diff / self.mzs
            ppmthreshold = defaults.DEFAULTS['reporterion_error'] * 1e-6
            return np.where(ppm < ppmthreshold)
        else:
            return np.where(diff < defaults.DEFAULTS['reporterion_error'])


@sequence.serializable("ReporterIonSummary")
class ReporterIonSummary(namedtuple("ReporterIonSummary",
    "ratio mz intensity")):
    '''Definitions for a report ion ratio summary'''

    _round = partial(round, ndigits=3)

    #  CLASS METHODS

    @classmethod
    def fromquery(cls, query, spectralwindow):
        '''Initializes the reporter ion summary from a query and mz window'''

        mz = np.zeros(query.mzs.size)
        intensity = np.zeros(query.mzs.size)

        indexes = ZIP(*query.where(spectralwindow.mz))
        for row, column in indexes:
            mz[row] = spectralwindow.mz[column]
            intensity[row] = spectralwindow.intensity[column]

        if intensity.any():
            ratio = intensity / intensity.max()
        else:
            ratio = intensity

        return cls(ratio.tolist(), mz.tolist(), intensity.tolist())

    #     PUBLIC

    def tostr(self, attr):
        return ':'.join([str(self._round(i)) for i in getattr(self, attr)])



# HELPERS
# -------


def ratiofromrow(query, row, rowdata):
    '''Returns a product ion ratio from a number'''

    if any(query.ions.name in i for i in rowdata['modifications'].unpack()):
        scan = row.linked.product.getscan(rowdata['num'])
        window = scan.masswindow(query.window)
        return ReporterIonSummary.fromquery(query, window)


# CORE
# ----


@logger.call('quantitative', 'debug')
@wrappers.runif(op.attrgetter('reporterions'))
@wrappers.threadprogress(53, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Quantifying reporter ions...")
def quantifyreporterions():
    '''Iterates over all rows to generate'''

    source = APP.discovererthread
    query = IonQuery.new()

    for row in source.files:
        reporter = []
        for index, rowdata in enumerate(row.data.iterrows(asdict=True)):
            reporter.append(ratiofromrow(query, row, rowdata))

        row.data['matched']['reporter'] = reporter
