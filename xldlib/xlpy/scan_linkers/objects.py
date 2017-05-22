'''
    XlPy/Scan_Linkers/objects
    _________________________

    Definitions for linked scan objects

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import multiprocessing

from collections import defaultdict
from functools import partial

from xldlib.definitions import MAP, ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import process


# ROW
# ---


@logger.init('linking', 'DEBUG')
class Row(base.BaseObject):
    '''Definitions for a file row's linked scans'''

    # ERRORS
    # ------
    error = False

    def __init__(self, row):
        super(Row, self).__init__()

        self.row = row

        self.precursor_to_product = self.prec = defaultdict(list)
        self.product_to_precursor = self.prod = defaultdict(list)
        self.index = defaultdict(list)

        self.checkprecursor = defaults.DEFAULTS['check_precursor']
        self.ppmthreshold = defaults.DEFAULTS['ppm_threshold'] * 1e-6

        self.precursor = self.row.spectra.getgroup('precursor')
        self.product = self.row.spectra.getgroup('product')

        self.setpool()

    def __call__(self, productnum):
        '''Appends the precursor and product scans to the row'''

        try:
            if productnum not in self.prod:
                product = self.product.getscan(str(productnum))
                for num, mz in self.find(productnum, product):
                    self.prec[num].append((productnum, mz))
                    self.prod[productnum].append(num)
        except KeyError:
            self.error = True

    #     SETTERS

    def setpool(self):
        '''Sets the pool/map for precursor scan linking'''

        # multiprocessing is ~50% slower than using a single core.
        if self.checkprecursor and defaults.DEFAULTS['use_multiprocessing']:
            cores = defaults.DEFAULTS['max_multiprocessing']
            self.pool = multiprocessing.Pool(processes=cores)
            self.mapper = self.pool.imap

        elif self.checkprecursor:
            self.mapper = MAP

    #     PUBLIC

    def group(self, key='precursor_num'):
        '''Groups scans by precursor number'''

        for index, num in enumerate(self.row.data['matched'][key]):
            self.index[num].append(index)

    def find(self, num, product):
        '''
        Searches scans starting from the nearest precursor, and including
        all with a 1-scan difference.
        '''

        if product.hasattr("precursor_num"):
            return [product.getattrs(['precursor_num', 'precursor_mz'])]
        elif self.checkprecursor:
            return self.findmatching(num, product)
        else:
            return self.findserial(num, product)

    def findserial(self, num, product):
        '''Returns the first scan in the precursor number list'''

        try:
            precursor_num = next(self.precursor.findscan(num))
            yield precursor_num, product.getattr('precursor_mz')
        except StopIteration:
            pass

    def findmatching(self, num, product):
        '''
        Returns all precursor scans with a matching product parent ion
        in the precursor m/z list.
        '''

        precursor_mz = product.getattr('precursor_mz')
        nums = list(self.precursor.findscan(num))
        mzs = (self.precursor.getscan(str(i)).mz[:] for i in nums)

        target = self.gettarget(precursor_mz)
        result = self.mapper(target, mzs)

        for precursor_num, bool_ in ZIP(nums, result):
            if bool_:
                yield precursor_num, precursor_mz

    def delevel(self):
        if self.row.ishierarchical():
            self.row.spectra.delevel()

    #     GETTERS

    def gettarget(self, precursor_mz):
        return partial(process.matchingprecursor,
            precursor_mz,
            self.ppmthreshold)
