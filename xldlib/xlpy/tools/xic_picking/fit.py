'''
    XlPy/Tools/Xic_Picking/fit
    __________________________

    Generic fitting algorithm which calls the currently selected
    XIC fitting or bounding algorithm and then further refines the
    properties by known biophysical parameters.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import multiprocessing
import operator as op
import weakref

from functools import reduce

#import numpy as np

from xldlib.definitions import MAP, ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.utils.xictools import scoring

from . import ab3d, cwt, xicfit


# HELPERS
# -------


@logger.init('peakpicking', 'DEBUG')
class FilterIsotopicLabels(base.BaseObject):
    '''
    Filters the isotopic labels included during peak fitting to those
    most likely to have tangible peak intensity, to remove noise during
    peak picking.
    '''

    def __init__(self):
        super(FilterIsotopicLabels, self).__init__()

        self.setfilterer()

    @logger.call('peakpicking', 'debug')
    def __call__(self, labels):
        return self.filterer(labels)

    #     SETTERS

    def setfilterer(self):
        '''Sets the default filtering function used for the class'''

        funname = "_filter{}".format(defaults.DEFAULTS['xic_filtering'])
        self.filterer = getattr(self, funname, self._filterall)

    #    FILTERERS

    def _filterid(self, labels):
        '''Uses only the isotope label for which the peptide was IDed'''

        populations = labels.getattr('sequenced_population')
        for crosslink in labels:
            if tuple(crosslink.getattr('populations')) in populations:
                yield crosslink

    def _filternomixing(self, labels):
        '''Uses only crosslinked peptides with homogeneous isotope labels'''

        for crosslink in labels:
            populations = crosslink.getattr('populations')
            if all(i == populations[0] for i in populations):
                yield crosslink

    def _filterall(self, labels):
        '''Uses all theoretical peptides'''

        for crosslink in labels:
            yield crosslink


def _intersection(charges):
    '''Returns the intersection of all the selected charges'''

    if len(charges) == 1:
        return charges[0][1]
    elif len(charges) > 1:
        reduced = [i[1] for i in charges]
        return reduce(set.intersection, reduced)
    else:
        return set()


@logger.init('peakpicking', 'DEBUG')
class ToggleSelection(base.BaseObject):
    '''
    Processes the selected transitions after calculating the fit scores
    associated with each transition.
    '''

    def __init__(self):
        super(ToggleSelection, self).__init__()

    #    PROPERTIES

    @property
    def xic_threshold(self):
        return defaults.DEFAULTS['xic_score_threshold']

    @property
    def equal_selection(self):
        return defaults.DEFAULTS['equal_crosslinks']

    @logger.call('peakpicking', 'debug')
    def __call__(self, labels):
        '''Selects all items recursively above certain score thresholds'''

        for crosslink in labels:
            for charge in crosslink:
                checkstate = self.getchecked(charge)
                charge.setattr('checked', checkstate, recurse=True)

            if not any(i.getattr('checked') for i in crosslink):
                # unselect only if all charges are not checked
                crosslink.setattr('checked', False)

        if self.equal_selection:
            charges = labels.get_checked_charges()
            # filter out the null values, since they can have no selection
            charges = [(i, j) for i, j in enumerate(charges) if j]
            selected = _intersection(charges)
            self.setequalselection(labels, charges, selected)

            # integrate after selecting items
            labels.set_integrated()

    #     SETTERS

    def setequalselection(self, labels, charges, selected):
        '''Sets an equal crosslinker selection among all selected crosslinks'''

        indexes = [i[0] for i in charges]
        for index in indexes:
            crosslink = labels[index]

            for charge in crosslink:
                checkstate = charge.levels.charge in selected
                charge.setattr('checked', checkstate, recurse=True)

    #     GETTERS

    def getchecked(self, charge):
        '''Returns if the charge exceeds all fit thresholds'''

        dotp = charge.getattr('dotp')
        mass = charge.get_masscorrelation()

        dotp_weight = 0.35
        size_weight = 0.2
        mass_weight = 0.45

        bounds = charge.get_crosslink().get_peak_indexes()
        size = scoring.get_size_weight(bounds.start, bounds.end)
        score = dotp * dotp_weight + mass_weight * mass + size_weight * size
        return score > self.xic_threshold


# PICKERS
# -------

PICKERS = {
    'ab3d': ab3d.boundab3d,
    'cwt': cwt.boundcwt
}


# PICKING
# -------


@logger.init('peakpicking', 'DEBUG')
class PickXics(base.BaseObject):
    '''
    Picks the XICs using one of various fitting algorithms and then
    weights for biophysical parameters, such as correlation with
    the isotope-labeled pair.
    '''

    def __init__(self):
        super(PickXics, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)

        self.pickfun = PICKERS[defaults.DEFAULTS['xic_picking']]
        self.selection = ToggleSelection()

        self.setlocked()
        self.setmapper()

    @logger.call('peakpicking', 'debug')
    def __call__(self):
        '''On start'''

        for transitionfile in self.source.transitions:
            items = {i: self.filterer(j) for i, j in enumerate(transitionfile)}
            fits = {k: MAP(xicfit.get_fitargs, v) for k, v in items.items()}
            bounds = {k: self.mapper(self.pickfun, v) for k, v in fits.items()}

            for index, bound in bounds.items():
                labels = transitionfile[index]
                self.setbounds(labels, bound)

                labels.calculate_fit()
                self.selection(labels)

        self._closepool()

    #     SETTERS

    def setlocked(self):
        '''
        Sets the current picking lock status and therefore the processing
        function.
        '''

        self.locked = self.source.transitions.getattr('retentiontime_lock')
        if self.locked:
            self.filterer = FilterIsotopicLabels()
        else:
            self.filterer = iter

    def setmapper(self):
        '''Sets the function mapping (either pool-based or within a process)'''

        # multiprocessing is ~10% slower than using a single core.
        if defaults.DEFAULTS['use_multiprocessing']:
            cores = defaults.DEFAULTS['max_multiprocessing']
            self.pool = multiprocessing.Pool(processes=cores)
            self.mapper = self.pool.imap
        else:
            self.mapper = MAP

    def setbounds(self, labels, bounds):
        '''Sets the XIC bounds for a given locked or unlocked peak'''

        if self.locked:
            bound = max(bounds, key=op.attrgetter('score'))
            self.setpeak(labels, bound)
        else:
            for crosslink, bound in ZIP(labels, bounds):
                self.setpeak(crosslink, bound)

    @staticmethod
    def setpeak(group, bound):
        '''Sets the start and end bounds for the group'''

        group.setattr('peak_start', bound.start)
        group.setattr('peak_end', bound.end)

    #     HELPERS

    def _closepool(self):
        if hasattr(self, "pool"):
            self.pool.close()
            self.pool.join()
