'''
    Export/Dataframes/base
    ______________________

    Inheritable base-class for dataframe instances.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import itertools as it
import operator as op

from collections import defaultdict, OrderedDict

import numpy as np

import six

from xldlib.definitions import re
from xldlib.objects.abstract.dataframe import DataFrameDict
from xldlib.resources.parameters import column_defs, defaults, reports
from xldlib.utils import decorators, logger, xictools


__all__ = [
    'Amplitudes',
    'Dataframe',
    'HierarchicalDataframe',
    'QuantitativeDataframe'
]


# CONSTANTS
# ---------

LOWER_SIGMA = u'\u03C3'
UPPER_SIGMA = u'\u03A3'


# REGEXES
# -------

NONQUANTIFIED = re.compile(u'<|>|-|{}'.format(xictools.INFINITY), re.UNICODE)


# DATA
# ----

CONCATENATED = {
    'report',
    'best_peptide',
    'best_peptide_file',
}

POLYPEPTIDE = {
    reports.LINKTYPES['interlink'],
    reports.LINKTYPES['multilink'],
}

MONOPEPTIDE = {
    reports.LINKTYPES['intralink'],
    reports.LINKTYPES['deadend'],
    reports.LINKTYPES['single'],
}

SORT_COLUMNS = [
    'Search Name',
    'Cross-Linker',
    'Precursor Scan',
    'Precursor RT',
    'Product Scan',
    'Product RT'
]

QUANTITATIVE_SORT_COLUMNS = [(' ', i) for i in SORT_COLUMNS]

# TEMPLATES
# ---------

POLYPEPTIDE_TEMPLATE = OrderedDict([
    ('intersubunit', 'Intersubunit {}'),
    ('intrasubunit', 'Intrasubunit {}'),
    ('greylist_intersubunit', 'Greylist Intersubunit {}'),
    ('greylist_intrasubunit', 'Greylist Intrasubunit {}'),
])

MONOPEPTIDE_TEMPLATE = OrderedDict([
    ('standard', 'Standard {}'),
    ('greylist', 'Greylist {}'),
])


# OBJECTS
# -------


class Subdataframe(DataFrameDict):
    '''Subdataframe object concatenated into the report'''

    def __init__(self, columns, sheet=None, title=None):
        super(Subdataframe, self).__init__(columns=columns)

        if sheet is not None:
            self.title = title.format(sheet.title)
        else:
            self.title = None



@logger.init('spreadsheet', level='DEBUG')
class Dataframe(DataFrameDict):
    '''Inheritable dataframe for shared methods'''

    def __init__(self, sheet, columns=None):
        super(Dataframe, self).__init__()

        self.sheet = sheet
        if columns is None:
            columns = column_defs.COLUMNS[sheet.name]
        self.columns = columns

    #     SETTERS

    def set_named_columns(self, columns):
        self.set_columns(self.getnamedcolumns(columns))

    def set_default_columns(self, dimensions=1):
        '''Sets the default columns in case no crosslinks identified'''

        self.dimensions = dimensions
        self.set_named_columns(self.columns.getordered(dimensions))

    def set_dimensions(self, crosslinks):
        '''Returns the maximum crosslink dimensions among the crosslinks'''

        previous = getattr(self, "dimensions", -1)
        dimensions = max(len(i.crosslink.index) for i in crosslinks)
        if dimensions > previous:
            self.dimensions = dimensions

            # for dependent dataframes
            if hasattr(self, "resize"):
                self.resize(previous)

    def set_subdataframes(self):
        '''Sets the temporary dataframe holder'''

        self.dataframes = OrderedDict()
        if self.sheet.name in CONCATENATED:
            if self.sheet.linktype in POLYPEPTIDE:
                for key, title in POLYPEPTIDE_TEMPLATE.items():
                    dataframe = Subdataframe(self.keys(), self.sheet, title)
                    self.dataframes[key] = dataframe

            elif self.sheet.linktype in MONOPEPTIDE:
                for key, title in MONOPEPTIDE_TEMPLATE.items():
                    dataframe = Subdataframe(self.keys(), self.sheet, title)
                    self.dataframes[key] = dataframe
        else:
            self.dataframes['report'] = Subdataframe(self.keys())

    def set_version(self):
        self.set_header()
        self.set_value()

    def set_linkagecounts(self, row, linkage):
        '''Adds the linkage counts to the current row'''

        if self.sheet.name == 'quantitative':
            self.__set_linkagecount(row, (' ', 'Counts Info'), linkage.count)
            self.__set_linkagecount(row, (' ', 'Counts Unique Info'), 1)

        else:
            self.__set_linkagecount(row, 'Counts Info', linkage.count)
            self.__set_linkagecount(row, 'Counts Unique Info', 1)

    def __set_linkagecount(self, row, column, count):
        '''Sets the counts for a given column'''

        if column in self:
            row[column] = count
        else:
            for index in range(self.dimensions):
                newcolumn = self.getcolumn(column, index)
                row[newcolumn] = count

    #     GETTERS

    def getcolumn(self, column, index):
        '''Returns the suffixed column'''

        suffix = self.columns.getsuffix(index)
        if isinstance(column, six.string_types):
            return column + suffix
        else:
            return column[0], column[1] + suffix

    def getnamedcolumns(self, columns):
        '''Returns the named spectral columns from a column list'''

        name = self.matched.reporterion.name
        if isinstance(columns, list):
            return [i.format(reporterion=name) for i in columns]
        elif isinstance(columns, dict):
            return {k.format(reporterion=name): v.format(reporterion=name)
                    for k, v in columns.items()}

    def __getsort(self, columns=SORT_COLUMNS, order=True):
        '''Returns the columns to sort by'''

        for name in columns:
            if name in self:
                yield (name, order)

            else:
                for index in range(self.dimensions):
                    newname = self.getcolumn(name, index)
                    if newname in self:
                        yield (newname, order)
                        break

    #     HELPERS

    def _concat(self):
        '''Concatenates the subfataframes into the current one'''

        for index, dataframe in enumerate(self.dataframes.values()):
            if dataframe.title is not None:
                self.set_value(value=dataframe.title)
            elif index:
                self.set_value()

            self.concat(dataframe)
            self.set_value()

    @logger.except_error(ValueError)
    def _sort(self, sort=None, **kwds):
        '''Sorts the subdataframes, ignoring the header'''

        if sort is None:
            sort = self.__getsort(**kwds)
        columns, order = zip(*sort)

        for dataframe in self.dataframes.values():
            if dataframe and next(iter(dataframe.values())):
                dataframe.sort(columns=columns, ascending=order)

    def _rename(self, dimensions):
        '''Returns a renamed dictionary with custom named'''

        rename = self.columns.getrename(dimensions)
        self.rename(rename)

    def _resize(self, previous):
        '''Resizes the dataframe dimensions for all the suffixed keys'''

        rename = self.columns.getresize(previous)
        renamed = self.getnamedcolumns(rename)

        columns = self.columns.getordered(self.dimensions)
        named = self.getnamedcolumns(columns)
        for dataframe in [self] + list(self.dataframes.values()):
            dataframe.rename(renamed)

            length = dataframe.get_last_index()
            dataframe.set_columns(named, length)
            dataframe._change_root(named)

    @staticmethod
    def _valuechecker(value, index=0):
        '''Normalizes the value for data export'''

        if isinstance(value, (list, tuple)):
            return value[index]
        return value


@logger.init('spreadsheet', level='DEBUG')
class MatchedDataframe(Dataframe):
    '''Definitions for a base dataframe with a matched object'''

    def __init__(self, matched, *args, **kwds):
        super(MatchedDataframe, self).__init__(*args, **kwds)

        self.matched = matched

    #     GETTERS

    def get_dataframe(self, data, linkage):
        '''Returns the temporary dataframe holder'''

        length = len(self.dataframes)
        if length == 1:
            return self.dataframes['report']
        elif length == 2 and linkage.greylist:
            return self.dataframes['greylist']
        elif length == 2:
            return self.dataframes['standard']
        elif length == 4 and linkage.greylist and linkage.intrasubunit:
            return self.dataframes['greylist_intrasubunit']
        elif length == 4 and linkage.greylist:
            return self.dataframes['greylist_intersubunit']
        elif length == 4 and linkage.intrasubunit:
            return self.dataframes['intrasubunit']
        else:
            return self.dataframes['intersubunit']

    def get_dataframe_row(self, data, crosslink):
        '''Processes the data into a singular row'''

        key = self.__get_spreadsheekey(crosslink)
        spreadsheet = data['spreadsheet'][key][crosslink.index]
        row = {}
        for column, values in spreadsheet.items():
            if column in self:
                row[column] = self._valuechecker(values)

            elif isinstance(values, (tuple, list)):
                for index, value in enumerate(values):
                    newcolumn = self.getcolumn(column, index)
                    row[newcolumn] = self._valuechecker(values, index)

        return row

    def __get_spreadsheekey(self, crosslink):
        '''Returns the spreadsheet key, dependent on the sheet type'''

        if type(crosslink).__name__ == 'Quantitative':
            return 'labeled'
        elif type(crosslink.crosslink).__name__ == 'Single':
            return 'singles'
        else:
            return 'crosslinks'

    #     HELPERS

    def _append(self, crosslink, linkage):
        '''Appends a new row to the dataframe for standard-like reports'''

        data = self.matched[crosslink.row]

        dataframe = self.get_dataframe(data, linkage)
        index = dataframe.get_last_index()
        row = self.get_dataframe_row(data, crosslink)

        if linkage not in self.seen:
            self.set_linkagecounts(row, linkage)
            self.seen.add(linkage)

        dataframe.loc[index] = row


# HIERARCHICAL
# ------------

ROW_TOTALS = (
    'Total Sum',
    'Total Count',
    'Total Interactions'
)


class HierarchicalDataframe(Dataframe):
    '''Definitions for dataframes with hierarchical headers'''

    #     COLUMNS

    def get2dfileheaders(self, linkages):
        '''Returns the current file header from the matched data'''

        filenames = sorted({i.file for i in linkages})
        crosslinkers = sorted({i.crosslinker for i in linkages})
        columns = [(j, ' '*i) for i, j in enumerate(self.ordered)]

        if self.columns.other['order'] == 'File':
            for filename in filenames:
                columns.extend((filename, i) for i in crosslinkers)
        else:
            for crosslinker in crosslinkers:
                columns.extend((crosslinker, i) for i in filenames)

        if getattr(self, "quantitative", False):
            for meth in ('getrationame', 'geterrorname'):
                columns.append((' ', ''))
                columns.extend((i, getattr(self, meth)()) for i in filenames)

        return columns

    #    COUNTS

    def setlinkagecounts(self, counts, index_memo):
        '''Stores the linkage counts for each file'''

        count_column = self.get_column(2)
        sum_column = self.get_column(3)

        for key, index in index_memo.items():
            self.loc[index, count_column] = counts.get_counts(key)
            self.loc[index, sum_column] = counts.get_sum(key)

    def setfilecounts(self, counts, headers=False, set_defaults=True):
        '''Stores the counts for each individual file and crosslinker'''

        index = self.get_last_index()
        firstcolumn = self.get_column()
        for offset, title in enumerate(ROW_TOTALS):
            self.loc[index+offset, firstcolumn] = title

        if headers:
            self.__setheadercounts(counts, index, headers)
        else:
            self.__setcounts(counts, index)

        if set_defaults:
            self.__setdefaults(index, counts)
        self.__settotals(index, counts)

    def __setheadercounts(self, counts, index, headers):
        '''Counts setter for ratio table objects'''

        for name in headers:
            for main in counts:
                key = (main, self.upper_sigma(name))
                self.loc[index, key] = counts.get_sum(main, name)
                self.loc[index+1, key] = counts.get_counts(main, name)
                self.loc[index+2, key] = counts.get_interactions(main, name)

    def __setcounts(self, counts, index):
        '''Count setter for single integer items as counts values'''

        for column in counts:
            self.loc[index, column] = counts.get_sum(column)
            self.loc[index+1, column] = counts.get_counts(column)
            self.loc[index+2, column] = counts.get_interactions(column)

    def __setdefaults(self, index, counts, default=0):
        '''Sets the default totals for each column'''

        missing = self.getmissing(counts)

        for column in missing:
            for offset in range(len(ROW_TOTALS)):
                self.loc[index+offset, column] = default

    def __settotals(self, index, counts):
        '''Adds the total sums for the current linkage type'''

        column = self.get_column(1)

        self.loc[index, column] = counts.get_totalsum()
        self.loc[index+1, column] = counts.get_totalcounts()
        self.loc[index+2, column] = counts.get_totalinteractions()

    def getmissing(self, counts):
        '''Returns the columns with no crosslinks identified'''

        length = len(self.ordered)
        missing = []
        for index, column in enumerate(self):
            if column == (' ', ''):
                # reaching ratio/error counts
                break

            if index >= length and column not in counts:
                missing.append(column)

        return missing

    #    HELPERS

    def upper_sigma(self, string):
        return self.__format(string, UPPER_SIGMA)

    def lower_sigma(self, string):
        return self.__format(string, LOWER_SIGMA)

    @staticmethod
    def __format(string, character):
        return u'{} ({})'.format(string, character)


# QUANTITATIVE
# ------------

# HELPERS
# -------


def getintegrated(spreadsheet, headers):
    return tuple(xictools.IntegralData.fromspreadsheet(
        spreadsheet, i) for i in headers)


# OBJECTS
# -------


class FileAmplitudes(defaultdict):
    '''Definitions for linkage amplitudes within a file'''

    def __init__(self, ratios, factory=set, *args, **kwds):
        super(FileAmplitudes, self).__init__(factory, *args, **kwds)

        self.range = 10**(defaults.DEFAULTS['intensity_filtering_range'])
        self.ratios = ratios

    def getmax(self):
        return max(self.ratios(i) for i in self.integratedvalues())

    def getmin(self):
        '''Returns the minimum intensity threshold when filtering'''

        return self.getmax() / self.range

    def integratedvalues(self):
        '''Generates an iterable over all the integrated values'''

        for linkage, integrated in self.integrateditems():
            yield integrated

    def integrateditems(self):
        '''Generate an iterable over all integrated items'''

        for linkage, values in self.items():
            for integrated in it.chain.from_iterable(values):
                yield linkage, integrated

    def labeleditems(self):
        '''Generate an iterable over all labeling items'''

        for linkage, values in self.items():
            for labels in values:
                yield linkage, labels


class Amplitudes(dict):
    '''Definitions for spectral amplitudes'''

    def __init__(self, ratios):
        super(Amplitudes, self).__init__()

        self.ratios = ratios

    #      PUBLIC

    def newfile(self, filename):
        self[filename] = file_obj = FileAmplitudes(self.ratios)
        return file_obj

    def checknew(self, filename):
        '''Analogous to setdefault'''

        if filename not in self:
            return self.newfile(filename)
        else:
            return self[filename]

    def filter(self):
        '''Checks to filter, and if so, filters the object'''

        return self.filterintensity().filtermetrics()

    def filterintensity(self, key='filter_transitions_byintensity'):
        return self.__filterer(key, self._filterintensity)

    def filtermetrics(self, key='filter_transitions_byscore'):
        return self.__filterer(key, self._filtermetrics)

    #    PROTECTED

    def __filterer(self, key, fun):
        '''If condition, filter by fun call, else, return unmodified obj'''

        if not defaults.DEFAULTS[key]:
            return self
        else:
            return fun()

    def _filterintensity(self):
        '''Returns items only above a certain intensity'''

        amplitudes = Amplitudes(self.ratios)
        for filename, file_obj in self.items():
            min_ = file_obj.getmin()

            newfile_obj = amplitudes.newfile(filename)
            for linkage, integrated in file_obj.labeleditems():
                if any(self.ratios(i) > min_ for i in integrated):
                    newfile_obj[linkage].add(integrated)

        return amplitudes

    def _filtermetrics(self):
        '''Returns only objects above a certain identification threshold'''

        amplitudes = Amplitudes(self.ratios)
        for filename, file_obj in self.items():
            newfile_obj = amplitudes.newfile(filename)
            for linkage, integrated in file_obj.labeleditems():
                if integrated[0].metrics.isabovethreshold():
                    newfile_obj[linkage].add(integrated)

        return amplitudes


class QuantitativeDataframe(Dataframe):
    '''Definitions for quantitative dataframe methods'''

    #      SETTERS

    def setratios(self, attr=None):
        '''Sets the defaiult ratios getter'''

        if attr is None:
            key = defaults.DEFAULTS['ratio_quantitation']
            attr = xictools.SPECTRAL_ENUM[key]
        self.attr = attr
        self.ratios = op.attrgetter(attr + '.value')

    #      GETTERS

    #     INTENSITY

    @decorators.overloaded
    def getamplitudes(self):
        '''Maps each linkage string to a a set of integrated data'''

        amplitudes = Amplitudes(self.ratios)

        for data in self.matched:
            file_obj = amplitudes.newfile(data['attrs']['search'])

            for index, crosslink in enumerate(data['labeledcrosslinks']):
                # get the integrated values
                spreadsheet = data['spreadsheet']['labeled'][index]
                headers = crosslink.getheaders(self.profile)
                integrated = getintegrated(spreadsheet, headers)

                # get the key
                linkage = spreadsheet.getlinkage()
                file_obj[linkage].add(integrated)

        return amplitudes.filter()

    #      RATIOS

    def getfiltered(self, linkages, ratios):
        '''Filter the linkages for those with quantifiable spectral ratios'''

        for linkage in linkages:
            if (linkage.file, linkage.string) in ratios:
                ratio = ratios[(linkage.file, linkage.string)]
                if isinstance(ratio.ratio, (list, tuple, np.ndarray)):
                    if not any(NONQUANTIFIED.search(i) for i in ratio.ratio):
                        # has a quantifiable ratio
                        yield linkage

    #     SPECTRAL

    def getratios(self, amplitudes):
        '''Generates the mean ratio and error for each of the amplitudes'''

        ratios = {}
        for filename in amplitudes:
            for linkage, integrated in amplitudes[filename].items():
                ratio = xictools.Ratios.fromintegrated(self.attr, *integrated)
                ratios[(filename, linkage)] = ratio.normalize(error=True)
        return ratios
