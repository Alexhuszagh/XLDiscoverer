'''
    Export/Dataframes/comparative
    _____________________________

    Dataframe producer for the comparative report, or a report
    with a 2D table of the crosslinks identified with a horizontal axis
    for files/crosslinkers and a vertical axis for linkages identified.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

from collections import Mapping, OrderedDict

import tables as tb

from xldlib.general import sequence
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import base, counters


# CONSTANTS
# ---------

COUNTS_MAP = {
    'Unique': 'unique',
    'Redundant': 'count',
}

LINKTYPES = OrderedDict([
    ('Intersubunit Links', lambda x: not op.attrgetter('intrasubunit')(x)),
    ('Intrasubunit Links', op.attrgetter('intrasubunit')),
])

# ENUMS
# -----

FLAGS = tb.Enum({
    'named': 2**0,
    'quantitative': 2**1,
    'filtered': 2**2,
})



# HELPERS
# -------


@logger.init('spreadsheet', level='DEBUG')
class ComparativeBase(base.QuantitativeDataframe, base.HierarchicalDataframe):
    '''
    Comparative dataframe creator, an independent report (does not
    depend on data from other reports).

    self.mode is a flag, with enumerations provided above
        0 -- standard comparative report
        1 -- standard comparative report
    '''

    def __init__(self, sheet, columns=None, flags=0):
        super(ComparativeBase, self).__init__(sheet, columns)

        self.ordered = self.columns.getordered(0)

        self.setflags(flags)
        self.setattrgetters()

    @logger.call('report', level='DEBUG')
    def __call__(self, crosslinks, alllinkages):
        '''Adds the crosslinks to the current dataframe on call'''

        linkages = self.getunique(alllinkages)

        self.set_columns(self.get2dfileheaders(linkages))
        self.set_version()
        self.loc[0, self.get_column(1)] = '{} Counts'.format(self.countsname)

        # use data pipelines
        ratios = None
        if self.quantitative:
            ratios = self.getratios(self.getamplitudes(crosslinks))

        if self.filtered:
            linkages = list(self.getfiltered(linkages, ratios))

        for title, fun in LINKTYPES.items():
            filtered = (i for i in linkages if fun(i))
            self.addlinkages(filtered, title, crosslinks, ratios)

        self._rename(0)

    def addlinkages(self, linkages, header, crosslinks, ratios):
        '''Adds the linkages and the counts information to the dataframe'''

        self.set_value(value=header)

        subunitmemo = set()
        index_memo = counters.IndexMemo(self)
        linkage_counts = counters.LinkageCounts(self.counter)
        file_counts = counters.FileCounts(self.counter)

        for linkage in linkages:
            # set the linkage information
            index = index_memo[linkage.string]
            column = self.getlinkagecolumn(linkage)
            self.loc[index, column] = self.counter(linkage)

            self.setsubunits(linkage, index, subunitmemo)

            # add row and file counts
            linkage_counts.setlinkage(linkage)
            file_counts.setlinkage(linkage, column)

            if self.quantitative:
                self.setamplitude(linkage, index, ratios)

        self.setlinkagecounts(linkage_counts, index_memo)
        self.setfilecounts(file_counts)
        self.set_value()

    #     SETTERS

    def setflags(self, flags):
        '''Set the flags for comparative generation fields'''

        self.named = bool(flags & FLAGS['named'])
        self.quantitative = bool(flags & FLAGS['quantitative'])
        self.filtered = bool(flags & FLAGS['filtered'])

    def setattrgetters(self):
        '''Set the attrgetters for namedtuple fields'''

        self.countsname = self.columns.other['counts']
        self.counter = op.attrgetter(COUNTS_MAP[self.countsname])
        self.setratios()

    def setsubunits(self, linkage, index, subunitmemo):
        '''Sets the subunit information for the linkage'''

        # set the subunit
        if linkage.subunits not in subunitmemo:
            column = self.get_column(0)
            self.loc[index, column] = linkage.getsubunit()
            subunitmemo.add(linkage.subunits)

    def setamplitude(self, linkage, index, ratios):
        '''Sets the amplitude data for each column, along with errors'''

        # need to check that the item is not from a partially labeled
        # identification.
        ratiocolumn = self.getratiocolumn(linkage)
        errorcolumn = self.geterrorcolumn(linkage)

        if (linkage.file, linkage.string) in ratios:
            ratio, error = ratios[(linkage.file, linkage.string)].tostr()

            self.loc[index, ratiocolumn] = ratio
            self.loc[index, errorcolumn] = error

        else:
            # item was sequenced, but was not quantified
            self.loc[index, ratiocolumn] = '-'
            self.loc[index, errorcolumn] = '-'

    #     GETTERS

    def getunique(self, linkages, fun=op.methodcaller('toseen')):
        '''Returns a unique set of the linkage set'''

        if isinstance(linkages, Mapping):
            exist = (i for i in linkages.values() if i.count)
        else:
            exist = (i for i in linkages if i.count)

        unique = sequence.uniquer(exist, idfun=fun)
        filtered = (i for i in unique if i.named or not self.named)
        return sorted(filtered, key=op.attrgetter('subunits', 'string'))

    #     COLUMNS

    def getlinkagecolumn(self, linkage):
        '''Returns the columns from the linkage'''

        if self.columns.other['order'] == 'File':
            return (linkage.file, linkage.crosslinker)
        else:
            return (linkage.crosslinker, linkage.file)

    def getratiocolumn(self, linkage):
        return (linkage.file, self.getrationame())

    @staticmethod
    def getrationame():
        return 'Ratio ({})'.format(defaults.DEFAULTS['xic_normalization'])

    def geterrorcolumn(self, linkage):
        return (linkage.file, self.geterrorname())

    @staticmethod
    def geterrorname():
        return 'StdDev ({})'.format(defaults.DEFAULTS['xic_normalization'])


# DATAFRAME
# ---------


@logger.init('spreadsheet', level='DEBUG')
class Dataframe(ComparativeBase):
    '''
    Comparative, quantitative dataframe exported from a transitions document.
    '''

    def __init__(self, matched, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.matched = matched
        self.profile = matched.profile
