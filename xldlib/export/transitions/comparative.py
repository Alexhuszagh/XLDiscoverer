'''
    Export/Transitions/comparative
    ______________________________

    Generates the quantitative, comparative dataframes and sheets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

from xldlib.definitions import ZIP
from xldlib.utils import logger

from . import base
from ..dataframes import comparative


# DATAFRAME
# ---------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(comparative.ComparativeBase, base.Dataframe):
    '''
    Comparative dataframe creator for transitions documents.

    self.mode is a flag, with enumerations provided above
        0 -- standard comparative report
        1 -- standard comparative report
    '''

    def __init__(self, profile, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.profile = profile


# WORKSHEETS
# ----------


@logger.init('spreadsheet', 'DEBUG')
class ComparativeWorksheets(base.WorksheetExport):
    '''Generates the worksheets for dataframe creation'''

    @logger.call('spreadsheet', 'debug')
    def __call__(self, document, flags=0):
        '''On call'''

        if isinstance(flags, six.string_types):
            flags = comparative.FLAGS[flags]
        elif isinstance(flags, (list, tuple)):
            flags = sum(comparative.FLAGS[i] for i in flags)
        # no key required, since the values are tuples of enums
        crosslinks = self.getcrosslinks(document)
        sheets = self.getsheets(crosslinks, sheet='quantitative_comparative')
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
