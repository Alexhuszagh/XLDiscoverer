'''
    Gui/Views/Visualizer/Trees/recalculate
    ______________________________________

    Tools for displaying PyQtGraph items.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np
from PySide import QtCore

from xldlib import exception
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger

from .. import base, styles

# CONSTANTS
# ---------
MUTEX = QtCore.QMutex()
LABELS_INDEX = 1
CROSSLINK_INDEX = 2


# RECALCULATE
# -----------


@logger.init('document', 'DEBUG')
class UpdateFitParameters(base.DocumentChild):
    '''Recalculates the fit metrics for the transitions'''

    # TIMER
    # -----

    def __init__(self, parent):
        super(UpdateFitParameters, self).__init__(parent)

        self.timer = QtCore.QTimer(singleShot=True)
        self.timer.timeout.connect(MUTEX.unlock)

        self.stylizer = styles.Stylizer('transition', parent)

    #    PROPERTIES

    @property
    @exception.except_error((AttributeError, KeyError))
    def locked(self):
        '''Attribute whether the retentiontime for the document is locked'''

        return self.document.retentiontime_lock

    @property
    def timeout(self):
        return defaults.DEFAULTS['graph_calculation_timeout']

    #  EVENT HANDLING

    @logger.call('document', 'debug')
    @decorators.overloaded
    def recalculate(self, group):
        '''Recalculates the displayed fit on a PyQtGraph linear region'''

        lock = MUTEX.tryLock()
        if lock:
            self.timer.start(self.timeout)
            self.widget.canvas.update_ppm(self.widget.peak)

            try:
                if self.locked:
                    self.recalculate_labels(group.get_labels())
                else:
                    self.recalculate_crosslink(group.get_crosslink())
            except (IndexError, TypeError):
                # returning the selected item is out of bounds, no document
                pass

    @logger.call('document', 'debug')
    @decorators.overloaded
    def store(self, group):
        '''Stores the new fit parameters on ending the pick'''

        try:
            if self.locked:
                group = group.get_labels()
                peak = group[0].get_peak_indexes()
                self.recalculate_labels(group, peak=peak)
            else:
                group = group.get_crosslink()
                peak = group.get_peak_indexes()
                self.recalculate_crosslink(group, peak=peak)

            # integrate data
            group.get_labels().set_integrated()
        except (IndexError, TypeError):
            # returning the selected item is out of bounds
            pass

    #     RECALCULATION

    def recalculate_labels(self, labels, peak=None):
        '''Recalculates the fit parameters for the labels children'''

        if peak is None:
            peak = self.widget.peak
        item = self.get_itemlevel(LABELS_INDEX + 1)

        for row in range(item.rowCount()):
            crosslink = labels[row]
            child = item.child(row)
            self.recalculate_crosslink(crosslink, child, peak=peak)

    def recalculate_crosslink(self, crosslink, item=None, peak=None):
        '''Recalculates the fit parameters for the crosslink children'''

        if item is None:
            item = self.get_itemlevel(CROSSLINK_INDEX + 1)
        if peak is None:
            peak = self.widget.peak

        for row in range(item.rowCount()):
            charge = crosslink[row]
            child = item.child(row)
            self.recalculate_charge(child, charge, peak)

    def recalculate_charge(self, item, charge, peak):
        '''Recalculates the dotp fit parameters for the charge'''

        dotp = np.mean(list(charge.get_dotp(peak)))
        self.stylizer.set_dotp(item, dotp)
        charge.setattr('dotp', dotp)

        for row in range(item.rowCount()):
            isotope = charge[row]
            child = item.child(row)
            self.recalculate_isotope(child, isotope, peak)

    def recalculate_isotope(self, item, isotope, peak):
        '''Recalculates the gaussian fit parameters for the charge'''

        gaussian = isotope.get_gaussian(peak)
        self.stylizer.set_gaussian(item, gaussian)
        isotope.setattr('gaussian', gaussian)

    #     HELPERS

    def get_itemlevel(self, index):
        '''Returns the item corresponding to the parent level'''

        modelindex = self.parent().selectedIndexes()[0]
        item = self.parent().model.itemFromIndex(modelindex)

        value = item.data()[index]
        while (value is not None) and (value != ''):
            item = item.parent()
            value = item.data()[index]

        return item
