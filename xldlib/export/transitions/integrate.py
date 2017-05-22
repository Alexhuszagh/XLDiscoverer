'''
    Export/Transitions/integrate
    ____________________________

    Generates the integrated dataframes and sheets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.definitions import ZIP
from xldlib.export import dataframes
from xldlib.utils import logger

from . import base


# DATAFRAMES
# -----------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(base.Dataframe):
    '''Export dataframe for the integrated parameters'''

    def __init__(self, profile, mixing, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.seen = set()
        self.ordered_columns = dataframes.OrderedMs1Columns(profile, mixing)

    def __call__(self, labels, linkage):
        '''Adds the label spreadsheet data to the current dataframe'''

        index = self.get_last_index()
        row = self.get_dataframe_row(labels.spreadsheet)

        if linkage not in self.seen:
            self.set_linkagecounts(row, linkage)
            self.seen.add(linkage)

        self.loc[index] = row

    #     SETTERS

    def set_version(self):
        self.set_header()
        self.set_value()

    def set_dimensions(self, lengths, dimensions):
        '''Returns the maximum crosslink dimensions among the crosslinks'''

        self.dimensions = dimensions
        columns = self.ordered_columns(self.columns, lengths, dimensions)
        self.set_columns(list(columns))

    #     GETTERS

    def get_dataframe_row(self, spreadsheet):
        '''Processes the data into a singular row'''

        row = {}
        for column, values in spreadsheet.items():
            if column in self:
                row[column] = self._valuechecker(values)

            elif isinstance(values, (tuple, list)):
                for index, value in enumerate(values):
                    newcolumn = self.getcolumn(column, index)
                    row[newcolumn] = self._valuechecker(values, index)

        return row


# WORKSHEETS
# ----------


class IntegratedWorkSheets(base.WorksheetExport):
    '''Generates the worksheets for dataframe creation'''

    @logger.call('spreadsheet', 'debug')
    def __call__(self, document):
        '''On call'''

        # no key required, since the values are tuples of enums
        crosslinks = self.getcrosslinks(document)
        sheets = self.getsheets(crosslinks)
        dataframes = self.getdataframes(sheets, document)

        self.process_dataframes(sheets, dataframes, crosslinks)

        return sheets, dataframes

    #     GETTERS

    def getdataframes(self, sheets, document):
        '''Initializes each dataframe for the integrated worksheets'''

        profile = document.profile
        mixing = document.include_mixed_populations
        return [Dataframe(profile, mixing, i) for i in sheets]

    #     HELPERS

    def process_dataframes(self, sheets, dataframes, crosslinks):
        '''Returns the dataframes generated for each sheet'''

        for sheet, dataframe in ZIP(sheets, dataframes):
            crosslink = base.Crosslink(sheet.linkname, sheet.linktype)
            labels_list = crosslinks[crosslink]

            lengths = {len(i.peptide) for i in labels_list}
            dimensions = max(lengths)
            dataframe.set_dimensions(lengths, dimensions)
            dataframe.set_version()

            linkages = self.getlinkages(labels_list)
            for labels, linkage in ZIP(labels_list, linkages):
                dataframe(labels, linkage)
