'''
    Export/Dataframes/report
    ________________________

    Dataframe producer for report, or the standard report.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.utils import logger

from . import base


# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(base.MatchedDataframe):
    '''
    Report dataframe creator, an independent report (does not depend
    on data from other reports).
    '''

    def __init__(self, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.seen = set()

    @logger.call('spreadsheet', 'debug')
    def __call__(self, crosslinks, linkages):
        '''Adds the crosslinks to the current dataframe on call'''

        self.set_dimensions(crosslinks)
        self.set_named_columns(self.columns.getordered(self.dimensions))

        self.set_version()
        self.set_subdataframes()

        for crosslink in crosslinks:
            linkage = linkages[(crosslink.row, crosslink.index)]
            self._append(crosslink, linkage)

        self._sort()
        self._concat()
        self._rename(self.dimensions)
