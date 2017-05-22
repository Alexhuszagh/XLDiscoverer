'''
    Export/Dataframes/ratiotable
    ____________________________

    Exports a ratio table, with a 2D header with the file names,
    the ratios (L/H), (M/H), etc exported as secondary columns.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import itertools as it
import operator as op

import tables as tb

import six

from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import base
from ..dataframes import comparative, counters

# load objects/functions
from xldlib.definitions import ZIP


# ENUMS
# -----

FLAGS = tb.Enum({
    'filtered': 2**0,
})


# HELPERS
# -------


def get_light(dimensions):
    '''Returns the numerators for ratios normalized to "Light" peptides'''

    if dimensions == 2:
        return ['H']
    elif dimensions == 3:
        return ['M', 'H']
    else:
        return ['M{}'.format(i) for i in range(1, dimensions-1)] + ['H']


def get_medium(dimensions):
    '''Returns the numerators for ratios normalized to "Medium" peptides'''

    if dimensions == 2:
        return get_heavy(dimensions), 'M'
    elif dimensions == 3:
        return ['L', 'H'], 'M'
    else:
        numerator = ['M{}'.format(i) for i in range(1, dimensions-2)]
        denominator = 'M{}'.format(dimensions-2)
        return numerator, denominator


def get_heavy(dimensions):
    '''Returns the numerators for ratios normalized to "Heavy" peptides'''

    if dimensions == 2:
        return ['L']
    elif dimensions == 3:
        return ['L', 'M']
    else:
        return ['L'] + ['M{}'.format(i) for i in range(1, dimensions-1)]


def get_variable(dimensions):
    '''Returns the numerators for ratios normalized to "Min" intensity'''

    if dimensions == 2:
        return ['L', 'H']
    elif dimensions == 3:
        return ['L', 'M', 'H']
    else:
        medium = ['M{}'.format(i) for i in range(1, dimensions-1)]
        return ['L'] + medium + ['H']


def get_ratio_labels(dimensions):
    '''Returns the numerators for the spectral labels'''

    normalize = defaults.DEFAULTS['xic_normalization']
    if normalize == 'Light':
        numerator = get_light(dimensions)
        denominator = 'L'
    elif normalize == 'Medium':
        numerator, denominator = get_medium(dimensions)
    elif normalize == 'Heavy':
        numerator = get_heavy(dimensions)
        denominator = 'H'
    elif normalize == 'Min':
        numerator = get_variable(dimensions)
        denominator = normalize
    else:
        numerator = get_variable(dimensions)
        denominator = normalize

    return ['{0}/{1}'.format(i, denominator) for i in numerator]


# DATAFRAMES
# ----------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(base.Dataframe, base.HierarchicalDataframe):
    '''Definitions for the ratio table dataframe'''

    def __init__(self, profile, sheet, flags, columns=None):
        super(Dataframe, self).__init__(sheet, columns)

        self.profile = profile
        self.ordered = self.columns.getordered(0)
        self.offset = 0
        if defaults.DEFAULTS['xic_normalization'] == 'Light':
            self.offset = -1

        self.setflags(flags)
        self.setattrgetters()
        self.setratios()

    def __call__(self, crosslinks, linkages):
        '''Adds the crosslinks to the current dataframe on call'''

        ratios = self.getratios(self.getamplitudes(crosslinks))
        if self.filtered:
            linkages = list(self.getfiltered(linkages, ratios))

        columns, ratioheaders = self.get2dfileheaders(crosslinks, linkages)
        self.set_columns(columns)
        self.set_version()

        for title, fun in comparative.LINKTYPES.items():
            items = (i for i in linkages if fun(i))
            filtered = sorted(items, key=op.attrgetter('string'))
            self.addlinkages(filtered, title, ratios, ratioheaders)

        self._rename(0)

    def addlinkages(self, linkages, header, ratios, ratioheaders):
        '''Adds the linkages and the counts information to the dataframe'''

        self.set_value(value=header)

        index_memo = counters.IndexMemo(self)
        linkage_counts = counters.LinkageCounts(self.counter)
        file_counts = counters.FileCounts(self.counter, ratioheaders)

        for linkage in linkages:
            if (linkage.file, linkage.string) in ratios:
                # no linkage in ratios if below threshold
                index = index_memo[linkage.string]
                self.loc[index, self.get_column(0)] = linkage.getsubunit()

                ratio_obj = self.getratio(linkage, ratios, ratioheaders)
                self.addratio(index, linkage, ratio_obj, ratioheaders)

                linkage_counts.setlinkage(linkage)
                file_counts.setlinkage(linkage, ratio_obj=ratio_obj)

        self.setlinkagecounts(linkage_counts, index_memo)
        self.setfilecounts(file_counts, ratioheaders, set_defaults=False)
        self.set_value()

    def addratio(self, index, linkage, ratio_obj, ratioheaders):
        '''Adds the ratios from a given linkage to the dataframe'''

         # set the ratio data
        zipper = ZIP(ratio_obj.ratio, ratio_obj.error)
        length = len(ratio_obj.ratio) - 1

        for idx, (ratiovalue, errorvalue) in enumerate(zipper):
            if idx != ratio_obj.index and idx < length:
                header = ratioheaders[self.offset + idx]
            elif idx != ratio_obj.index and idx == length:
                header = ratioheaders[-1]
            else:
                continue

            # TODO: clean this up... the ratioobj should have this builtin
            try:
                ratiovalue = float(ratiovalue)
            except ValueError:
                pass
            try:
                errorvalue = float(errorvalue)
            except ValueError:
                pass

            ratiocolumn = self.getratiocolumn(linkage, header)
            self.loc[index, ratiocolumn] = ratiovalue

            errorcolumn = self.geterrorcolumn(linkage, header)
            self.loc[index, errorcolumn] = errorvalue

            counts = ratio_obj.getcounts(idx)
            countscolumn = self.getcountscolumn(linkage, header)
            self.loc[index, countscolumn] = counts

    #     SETTERS

    def setflags(self, flags):
        '''Set the flags for the ratiotable export'''

        self.filtered = bool(flags & FLAGS['filtered'])

    def setattrgetters(self):
        '''Set the attrgetters for namedtuple fields'''

        self.countsname = self.columns.other['counts']
        self.counter = op.attrgetter(comparative.COUNTS_MAP[self.countsname])

    #     GETTERS

    #     HEADERS

    def get2dfileheaders(self, crosslinks, linkages):
        '''Returns the appropriate file headers for the current linkages'''

        filenames = sorted({i.file for i in linkages})
        columns = [(j, ' '*i) for i, j in enumerate(self.ordered)]
        ratioheaders = self.getratioheaders(crosslinks)

        if self.columns.other['order'] == 'File':
            iterable = it.product(filenames, ratioheaders)
        else:
            iterable = it.product(ratioheaders, filenames)

        for main, sub in iterable:
            for fun in (str, self.lower_sigma, self.upper_sigma):
                columns.append((main, fun(sub)))

        return columns, ratioheaders

    def getratioheaders(self, crosslinks):
        '''Returns the ratio headers as a function of the crosslink size'''

        dimensions = 0
        if crosslinks:
            dimensions = max(len(i.getheaders()) for i in crosslinks)

        if not dimensions:
            return []
        elif dimensions == 1:
            return ['Label Free']
        else:
            return get_ratio_labels(dimensions)

    #     RATIOS

    def getratio(self, linkage, ratios, ratioheaders):
        '''Returns the ratio as an array and the '''

        ratio_obj = ratios[(linkage.file, linkage.string)]
        ratio = ratio_obj.ratio
        if isinstance(ratio, six.string_types):
            ratio = [ratio] * (len(ratioheaders) + 1)

        error = ratio_obj.error
        if isinstance(error, six.string_types):
            error = [error] * (len(ratioheaders) + 1)

        return ratio_obj._replace(ratio=ratio, error=error)

    #     COLUMNS

    def getratiocolumn(self, linkage, header):
        return self.getcolumn(linkage, header, str)

    def geterrorcolumn(self, linkage, header):
        return self.getcolumn(linkage, header, self.lower_sigma)

    def getcountscolumn(self, linkage, header):
        return self.getcolumn(linkage, header, self.upper_sigma)

    def getcolumn(self, linkage, header, fun):
        '''Returns the column name from the string'''

        if self.columns.other['order'] == 'File':
            return (linkage.file, fun(header))
        else:
            return (header, fun(linkage.file))


# WORKSHEETS
# ----------


class RatioTableWorksheets(base.WorksheetExport):
    '''Generates the worksheets for dataframe creation'''

    @logger.call('spreadsheet', 'debug')
    def __call__(self, document, flags=0):
        '''On call'''

        if isinstance(flags, six.string_types):
            flags = FLAGS[flags]
        elif isinstance(flags, (list, tuple)):
            flags = sum(FLAGS[i] for i in flags)

        crosslinks = self.getcrosslinks(document)
        sheets = self.getsheets(crosslinks, sheet='ratiotable')
        dataframes = self.getdataframes(sheets, document, flags)

        self.process_dataframes(sheets, dataframes, crosslinks)

        return sheets, dataframes

    #     GETTERS

    def getdataframes(self, sheets, document, flags):
        '''Initializes each dataframe for the integrated worksheets'''

        profile = document.profile
        return [Dataframe(profile, i, flags=flags) for i in sheets]

    #     HELPERS

    def process_dataframes(self, sheets, dataframes, crosslinks):
        '''Returns the dataframes generated for each sheet'''

        for sheet, dataframe in ZIP(sheets, dataframes):
            crosslink = base.Crosslink(sheet.linkname, sheet.linktype)
            labels_list = crosslinks[crosslink]
            linkages = self.getlinkages(labels_list)

            dataframe(labels_list, linkages)
