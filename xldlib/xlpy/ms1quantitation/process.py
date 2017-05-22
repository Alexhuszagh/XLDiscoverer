'''
    XlPy/MS1Quantitation/process
    ____________________________

    Processes the extracted ion chromatograms (XICs), including XIC
    fitting or bounding.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import weakref

from xldlib.objects import documents
from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.xlpy.tools import xic_picking
from xldlib.xlpy import wrappers


# HELPERS
# -------


def calculatesignalnoise(hdf5group):
    '''Calculates the average noise over the entire chromatogam'''

    y = hdf5group.intensity()
    baseline = xic_picking.calculate_baseline(y)
    hdf5group.setattr('baseline', baseline)

    noise = xic_picking.calculate_noise(y)
    hdf5group.setattr('noise', noise)


# PROCESSING
# ----------


@logger.init('quantitative', 'DEBUG')
class ProcessXics(base.BaseObject):
    '''Processes the extracted ion chromatogams and bounds or fits the XICs'''

    def __init__(self):
        super(ProcessXics, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)
        self.document = weakref.proxy(self.source.transitions)

        self.picker = xic_picking.PickXics()
        self.sorter = documents.DocumentSorter('transition', self)

    @logger.call('quantitative', 'debug')
    def __call__(self):
        '''On start'''

        self.setsignalnoise()
        self.picker()
        self.sorter()

        self.source.pause('transition')

    #     SETTERS

    def setsignalnoise(self):
        '''
        Sets the signal to noise constants and integrates the intensity
        for each spectral level.
        '''

        for transitionfile in self.source.transitions:
            for labels in transitionfile:
                for crosslinks in labels:
                    for charges in crosslinks:
                        for isotope in charges:
                            calculatesignalnoise(isotope)
                        # do our serial appending to sum each iteration
                        calculatesignalnoise(charges)
                    calculatesignalnoise(crosslinks)
                calculatesignalnoise(labels)
            calculatesignalnoise(transitionfile)


@logger.call('quantitative', 'debug')
@wrappers.runif(op.attrgetter('quantitative'))
@wrappers.threadprogress(130, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Processing XICs...")
def processxics():
    inst = ProcessXics()
    inst()
