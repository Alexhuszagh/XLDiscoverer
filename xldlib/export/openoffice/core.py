'''
    Export/OpenOffice/core
    ______________________

    Core writer to the Open Office data format, which integrates various
    engines into a common interface.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import sys

from xldlib.export import dataframes
from xldlib.objects import protein
from xldlib.qt.objects import base
from xldlib.resources import paths
from xldlib.resources.parameters import reports
from xldlib.utils import logger
from xldlib.xlpy import wrappers


# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class OpenOfficeWriter(base.BaseObject):
    '''Core Open Office format writer'''

    def __init__(self, path=paths.FILES['spreadsheet']):
        super(OpenOfficeWriter, self).__init__()

        self.set_engine()
        self.workbook = self.engine.Workbook(path)

    #     SETTERS

    def set_engine(self):
        '''Sets the Open Office engine for the writer'''

        if 'xlsxwriter' in sys.modules:
            from . import xlsxwriter_
            self.engine = xlsxwriter_

        # xlsxwriter distributed, uncomment if you want to use OpenPyXl
        #elif 'openpyxl' in sys.modules:
        #    from . import openpyxl_
        #    self.engine = openpyxl_


# MATCHED
# -------


@logger.init('spreadsheet', 'DEBUG')
class MatchedWriter(OpenOfficeWriter):
    '''Writes the matched session data to file'''

    def __init__(self, matched, proteins):
        super(MatchedWriter, self).__init__()

        self.matched = matched

        self.sheets = reports.REPORTS.getsheets()
        self.creator = dataframes.DataframeCreator(self.matched, proteins,
                                                   self.sheets)
        self.dependents = {}

    #  CLASS METHODS

    @classmethod
    def fromsource(cls):
        '''Initializes the exporter from a working thread'''

        source = cls.app.discovererthread
        return cls(source.matched, source.proteins)

    @classmethod
    def frommatched(cls, matched):
        '''Initializes the exporter from a working thread'''

        proteins = protein.ProteinTable(tryopen=True, set_mapping=True)
        return cls(matched, proteins)

    @logger.call('report', 'DEBUG')
    def __call__(self):
        '''Creates the independent and dependent sheets'''

        for index, sheet in enumerate(self.sheets):
            if self._checkskip(sheet):
                continue
            elif sheet.type == reports.REPORT_TYPES['independent']:
                dataframe = self.creator(sheet)
                self.workbook.add_worksheet(index, sheet.title, dataframe)

            elif sheet.type == reports.REPORT_TYPES['dependent']:
                worksheet = self.workbook.add_worksheet(index, sheet.title)
                dataframe = self.creator.dependents[sheet.name]
                self.dependents[index] = (worksheet, dataframe)

        for index, (worksheet, dataframe) in self.dependents.items():
            dataframe.finish()
            worksheet.setdataframe(dataframe)

        self.workbook.save()

    #    HELPERS

    def _checkskip(self, sheet):
        '''Checks if the dataframe is conditional and turned off'''

        return any((
            (sheet.name in {'quantitative', 'quantitative_comparative'}
                and not self.matched.quantitative),
            (sheet.linkname == reports.LINKNAMES['Fingerprint']
                and not self.matched.fingerprinting),
            ))


@logger.call('spreadsheet', 'debug')
@wrappers.threadprogress(80, 1, condition=id)
@wrappers.threadmessage("Creating Open Office workbook...")
def writematched():
    '''Writes the matched session data to file'''

    inst = MatchedWriter.fromsource()
    inst()
