'''
    Export/Transitions/core
    _______________________

    Core processor for exporting transitions to OpenOffice spreadsheets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.definitions import ZIP
from xldlib.qt.objects import base

from . import comparative, integrate, ratiotable, transitions
from .. import openoffice


# EXPORTER
# --------


class Exporter(base.BaseObject):
    '''Exporter definitions and methods'''

    def __init__(self):
        super(Exporter, self).__init__()

        self._integrate = integrate.IntegratedWorkSheets()
        self._transitions = transitions.TransitionWorkSheets()
        self._comparative = comparative.ComparativeWorksheets()
        self._ratiotable = ratiotable.RatioTableWorksheets()

    def __call__(self, document, path, sheets, dataframes):
        '''On call'''

        writer = openoffice.OpenOfficeWriter(path)
        zipped = ZIP(sheets, dataframes)
        for index, (sheet, dataframe) in enumerate(zipped):
            writer.workbook.add_worksheet(index, sheet.title, dataframe)
        writer.workbook.save()

    #    PUBLIC

    def integrate(self, document, path):
        '''Integrates and sums all the transitions and exports a full report'''

        sheets, dataframes = self._integrate(document)
        self(document, path, sheets, dataframes)

    def area(self, document, path):
        '''Exports a transiiton list with the intensities for each isotope'''

        sheets, dataframes = self._transitions(document, key='area')
        self(document, path, sheets, dataframes)

    def intensity(self, document, path):
        '''Exports a transiiton list with the intensities for each isotope'''

        sheets, dataframes = self._transitions(document, key='ymax')
        self(document, path, sheets, dataframes)

    def comparative(self, document, path):
        '''Exports a quantitative comparative report'''

        sheets, dataframes = self._comparative(document, flags='quantitative')
        self(document, path, sheets, dataframes)

    def filteredcomparative(self, document, path):
        '''Exports a quantitative comparative report filtered for ratios'''

        flags = ('quantitative', 'filtered')
        sheets, dataframes = self._comparative(document, flags)
        self(document, path, sheets, dataframes)

    def ratiotable(self, document, path):
        '''Exports a table with all ratios, quantifiable or not'''

        sheets, dataframes = self._ratiotable(document)
        self(document, path, sheets, dataframes)

    def filteredratiotable(self, document, path):
        '''Exports a ratio table with all quantifiable ratios'''

        sheets, dataframes = self._ratiotable(document, flags='filtered')
        self(document, path, sheets, dataframes)
