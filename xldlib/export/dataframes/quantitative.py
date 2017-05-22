'''
    Export/Dataframes/quantitative
    ______________________________

    Dataframe producer for the quantitative report, or standard report
    with data included for extracted ion chromatogram integration.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

import tables as tb

from xldlib.definitions import ZIP
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import base


# ENUMS
# -----

ColumnTypes = tb.Enum([
    'null',
    'labeled'
])


# HELPERS
# -------


@logger.init('spreadsheet', 'DEBUG')
class OrderedMs1Columns(object):
    '''
    Returns ordered, grouped MS1 columns as a series of tuples
    for a hierarchical header.
    '''

    def __init__(self, profile, mixing):
        super(OrderedMs1Columns, self).__init__()

        self.profile = profile
        self.mixing = mixing

    #  CLASS METHODS

    @classmethod
    @logger.call('spreadsheet', 'debug')
    def frommatched(cls, matched):
        '''Returns a formatter from a matched data class'''

        mixing = defaults.DEFAULTS['include_mixed_populations']
        return cls(matched.profile, mixing)

    #     MAGIC

    def __call__(self, columns, lengths, dimensions, fun=op.attrgetter('key')):
        '''Returns the columns from a series of labels'''

        labels = self.profile.getheaders(lengths, self.mixing)

        for block in columns.blocks:
            columnseries = block.getseries()

            for series in columnseries:
                subblock = block._replace(columns=series.columns)
                ordered = columns.getblock(subblock, dimensions, fun)
                for label, column in ordered.getlabeled(labels, series):
                    yield label, column

    #    GETTERS

    def getrename(self, columns, lengths, dimensions):
         '''Returns a rename dictionary with each original name to newname'''

         original = self(columns, lengths, dimensions)
         new = self(columns, lengths, dimensions, fun=op.attrgetter('name'))
         return {k: v for k, v in ZIP(original, new) if k != v}


# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(base.MatchedDataframe):
    '''
    Quantitative dataframe creator, an independent report (does not
    depend on data from other reports).
    '''

    def __init__(self, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.seen = set()
        self.orderedcolumns = OrderedMs1Columns.frommatched(self.matched)

    @logger.call('spreadsheet', 'debug')
    def __call__(self, crosslinks, linkages):
        '''Adds the crosslinks to the current dataframe on call'''

        standardcrosslinks = list(self._convertcrosslinks(crosslinks))
        self.set_dimensions(standardcrosslinks)
        self._setcolumns(crosslinks)

        self.set_version()
        self.set_subdataframes()

        for crosslink in crosslinks:
            linkage = linkages[(crosslink.row, crosslink.index)]
            self._append(crosslink, linkage)

        self._sort(columns=base.QUANTITATIVE_SORT_COLUMNS)
        self._concat()
        self._rename(crosslinks)

    #     SETTERS

    def _setcolumns(self, crosslinks):
        '''Sets the columns for the dataframes'''

        lengths = self.get_lengths(crosslinks)
        columns = self.orderedcolumns(self.columns, lengths, self.dimensions)
        self.set_columns(list(columns))

    #     GETTERS

    def get_lengths(self, crosslinks):
        return {len(i.crosslink.sequenced) for i in crosslinks}

    #     HELPERS

    def _convertcrosslinks(self, crosslinks):
        '''Converts the crosslinks to the proper object type'''

        for crosslink in crosslinks:
            index = crosslink.index
            data = self.matched[crosslink.row]
            yield crosslink._replace(crosslink=data['crosslinks'][index])

    def _rename(self, crosslinks):
        '''Returns a renamed dictionary with custom named'''

        lengths = self.get_lengths(crosslinks)
        rename = self.orderedcolumns.getrename(self.columns, lengths,
                                               self.dimensions)
        self.rename(rename)

