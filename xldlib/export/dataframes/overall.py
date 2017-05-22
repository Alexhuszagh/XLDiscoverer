'''
    Export/Dataframes/overall
    _________________________

    Dataframe producer for the overall, or general report.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.utils import logger

from . import base


# SORTING
# -------

SORTKEY = [
    ('Double', False),
    ('Intersubunit', False),
    ('Intrasubunit', False),
    ('Deadend', False),
    ('Single', True),
    ('Intralink', True)
]


# OBJECTS
# -------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(base.MatchedDataframe):
    '''
    Overall dataframe creator, a dependent report (depends on data
    from other reports).
    '''

    def __init__(self, *args, **kwds):
        super(Dataframe, self).__init__(*args, **kwds)

        self.set_default_columns()
        self.set_version()
        self.set_subdataframes()

        self.seen = set()

    @logger.call('report', 'DEBUG')
    def __call__(self, crosslinks, linkages):
        '''Adds the crosslinks to the current dataframe on call'''

        self.set_dimensions(crosslinks)
        for crosslink in crosslinks:
            linkage = linkages[(crosslink.row, crosslink.index)]
            self._append(crosslink, linkage)

    #     HELPERS

    def finish(self):
        self._sort(sort=SORTKEY)
        self._concat()
        self._rename(self.dimensions)

    def resize(self, previous):
        self._resize(previous)
