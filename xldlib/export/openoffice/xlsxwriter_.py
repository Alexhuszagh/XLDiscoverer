'''
    Export/OpenOffice/xlsxwriter_
    _____________________________

    XlsxWriter engine for the Open Office writer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import xlsxwriter

from xldlib.utils import decorators, logger

from . import base


# FORMATS
# -------

HEADER = {
    'bold': True,
    'underline': 1,
    'align': 'center'
}

# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class Worksheet(base.Worksheet):
    '''Standardized worksheet object for OpenPyXl'''

    def __init__(self, worksheet, workbook):
        super(Worksheet, self).__init__(worksheet, workbook)

        self.header = self.workbook.add_format('header', HEADER)

    #  INITIALIZERS

    @classmethod
    @logger.call('spreadsheet', 'debug')
    def new(cls, workbook, title):
        worksheet = workbook.create_sheet(title)
        return cls(worksheet, workbook)

    #     SETTERS

    def set_columnsizes(self, dataframe, columns):
        '''Sets the sizes for each column in the sheet'''

        for index, key in enumerate(dataframe):
            data = columns.get(key)
            if data is not None:
                # predefined column
                formatting = self.workbook.add_format(key, data.formatting)
                self.worksheet.set_column(index, index, data.size, formatting)

    @decorators.overloaded
    def set_styles(self, dataframe):
        '''Writes the XlsxWriter styles to cell prior to adding data'''

        for row in range(self.columnlength):
            self.worksheet.set_row(row, None, self.header)

    def set_padding(self):
        '''Null method for compatability with OpenPyXl engine'''

    #    WRITERS

    @decorators.overloaded
    def _write_cell(self, row, column, value):
        '''Writes a value to an OpenPyXl cell'''

        self.worksheet.write(row, column, value)

    #  PUBLIC FUNCTIONS

    def merge(self, first_row, first_column, last_row, last_column, data):
        '''Provides a merge range for the worksheet'''

        if data and data != ' ':
            self.worksheet.merge_range(first_row, first_column, last_row,
                last_column, data, self.header)


@logger.init('spreadsheet', 'DEBUG')
class Workbook(base.Workbook):
    '''Workbook object for the Open Office writer'''

    def __init__(self, path):
        super(Workbook, self).__init__(path)

        self.workbook = xlsxwriter.Workbook(path)
        self.formats = {}

    #     MAGIC

    def __getitem__(self, index):
        '''Workbook[index] -> Worksheet'''

        worksheet = self.workbook.worksheets()[index]
        return Worksheet(worksheet, self)

    #  PUBLIC FUNCTIONS

    def add_worksheet(self, index, title, dataframe=None):
        '''Adds a worksheet to the workbook at the given index'''

        title = self._titlechecker(title)
        worksheet = Worksheet.new(self, title)
        if dataframe is not None:
            worksheet.setdataframe(dataframe)
        return worksheet

    def create_sheet(self, title):
        return self.workbook.add_worksheet(title)

    def add_format(self, key, mapping):
        '''Adds and memoizes a new workbook formatter'''

        if key not in self.formats:
            self.formats[key] = self.workbook.add_format(mapping)

        return self.formats[key]

    def save(self):
        self.workbook.close()
