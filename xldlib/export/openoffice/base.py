'''
    Export/OpenOffice/base
    ______________________

    Inheritable methods for Open Office writers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import itertools as it
import operator as op

import six

from xldlib.qt.objects import base
from xldlib.utils import logger, math_

# HELPERS
# -------


def notnull(value):
    '''Returns if a False if value is numpy.nan or is only whitespace'''

    if isinstance(value, six.string_types):
        # null string
        return bool(value.strip())
    else:
        # null number
        return not math_.isnull(value)


# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class Worksheet(base.BaseObject):
    '''Shared methods between Worksheet classes'''

    def __init__(self, worksheet, workbook):
        super(Worksheet, self).__init__()

        self.worksheet = worksheet
        self.workbook = workbook

    #    SETTERS

    def setdataframe(self, dataframe):
        '''Adds a dataframe to the current worksheet'''

        if dataframe.columns is not None:
            columns = dataframe.columns.asdict()
        else:
            columns = {}

        self.set_columnlength(dataframe)
        self.set_styles(dataframe, columns)

        self.set_columnsizes(dataframe, columns)
        self.set_header(dataframe)
        self.set_data(dataframe)
        self.set_padding()

    def set_columnlength(self, dataframe):
        '''Sets the length of the dataframe columns, IE, the header length'''

        column = dataframe.get_column()
        if isinstance(column, tuple):
            self.columnlength = len(column)
        else:
            self.columnlength = 1

    def set_header(self, dataframe):
        '''Sets the header for the spreadsheet'''

        if self.columnlength == 1:
            self.__set_flatheader(dataframe)
        else:
            self.__set_hierarchicalheader(dataframe)

    def __set_flatheader(self, dataframe):
        '''Sets a header with only a single row of values'''

        for index, column in enumerate(dataframe):
            self.write_cell(0, index, column)

    def __set_hierarchicalheader(self, dataframe):
        '''Sets a header with multiple rows of values'''

        counter = 0
        grouped = it.groupby(dataframe, key=op.itemgetter(0))
        grouped = (tuple(v) for k, v in grouped)
        for group in grouped:

            if len(group) > 1:
                merge = True
                mergestart = counter
            else:
                merge = False

            for index, column in enumerate(group):
                # no row/col 0, 1-indexes
                if index == 0 and not merge:
                    self.write_cell(0, counter, column[0])
                self.write_cell(1, counter, column[1])

                counter += 1

            if merge:
                data = group[0][0]
                self.merge(0, mergestart, 0, counter-1, data)

    def set_data(self, dataframe):
        '''Writes the data from the dataframe to the worksheet'''

        for index, (column, column_values) in enumerate(dataframe.items()):
            for row, value in enumerate(column_values):
                self.write_cell(row+self.columnlength, index, value)

    #    WRITERS

    def write_cell(self, row, column, value, header=False):
        '''Writes a value to an Open Office cell'''

        if notnull(value):
            self._write_cell(row, column, value, header)


@logger.init('spreadsheet', 'DEBUG')
class Workbook(base.BaseObject):
    '''Shared methods between Workbook classes'''

    def __init__(self, path):
        super(Workbook, self).__init__()

        self.path = path

    #    HELPERS

    @staticmethod
    def _titlechecker(title, max_characters=31, truncated=14):
        if len(title) > max_characters:
            return title[:truncated] + '...' + title[-truncated:]
        return title
