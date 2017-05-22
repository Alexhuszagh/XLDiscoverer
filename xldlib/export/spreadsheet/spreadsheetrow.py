'''
    Export/Spreadsheet/spreadsheetrow
    _________________________________

    Base object for generating spreadsheet data rows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.qt.objects import base

# DATA
# ----

ATTR_TYPES = {
    'search': "Search Name",
    'fraction': "File Name",
    'project': "Project Name",
    'ms1': "MS1 Scans Name",
    'scans': "MS Scans Name",
    'precursor': "Precursor Scans Name",
    'product': "Product Scans Name",
    'matched': "Matched Output Name",
    'runtime': "Runtime"
}

DATA_TYPES = {
    'num': "Product Scan",
    'peptide': "DB Peptide",
    'start': "Start",
    'id': "Subunit",
    'name': "Subunit Name",
    'preferred': "Common/Gene Name",
    'mz': "MS3 m/z",
    'z': "MS3 z",
    'ppm': "MS3 PPM",
    'score': "MS3 Score",
    'ev': "MS3 EV",
    'rank': "Search Rank",
    'precursor_num': "Precursor Scan",
    'precursor_rt': "Precursor RT",
    'precursor_mz': "MS2 m/z",
    'precursor_z': "MS2 z",
    # MS1 data is added after data extraction
    # 'ms1_num': "MS1 Scan",
    # 'ms1_rt': "MS1 RT"
}

REPORTER_TYPES = {
    'ratio': "{reporterion} Ratios",
    'mz': "{reporterion} m/z",
    'intensity': "{reporterion} Intensity",
}

# BASE
# ----


class SpreadsheetRow(base.BaseObject):
    '''Shared methods for processing invididual rows of spreadsheet data'''

    def __init__(self, row):
        super(SpreadsheetRow, self).__init__()

        self.row = row

        source = self.app.discovererthread
        self.reporterion = source.matched.reporterion.name

    #    SETTERS

    def setattrs(self, values):
        '''Sets the file data for a given scan'''

        for key, column in ATTR_TYPES.items():
            values[column] = [self.row.data['attrs'].get(key, '')]

    def setdata(self, values, indexes):
        '''Converts the variable length array types to spreadsheet values'''

        for key, column in DATA_TYPES.items():
            values[column] = list(self.row.data.getcolumn(indexes, key))

    def setreporter(self, values, indexes):
        '''Converts the report ion data to spreadsheet values'''

        items = list(self.row.data.getcolumn(indexes, 'reporter'))
        for key, column in REPORTER_TYPES.items():
            strs = [i.tostr(key) if i is not None else '' for i in items]
            formatted = column.format(reporterion=self.reporterion)
            values[formatted] = strs

    def setreporternull(self, values, indexes):
        '''Sets null values if report ion quantitation is inactive'''

        for key, column in REPORTER_TYPES.items():
            formatted = column.format(reporterion=self.reporterion)
            values[formatted] = [float('nan')] * len(indexes)
