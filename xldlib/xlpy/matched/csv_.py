'''
    XlPy/matched/csv_
    _________________

    Inheritable class to parse structured text file formats (
    tab-delimited text, CSV), ensure data integrity, and type-cast
    the data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import csv
import operator as op
import types

from xldlib import exception
from xldlib.qt.objects import base
from xldlib.utils import logger

# load objects/functions
from xldlib.definitions import partial


# CONVERSION
# ----------


def castzero(item, cast=str, getter=op.itemgetter(0)):
    return cast(getter(item))


PROCESS = {
    "start": partial(castzero, cast=int),
    "name": partial(castzero, cast=str),
    "mz": partial(castzero, cast=float),
    "z": partial(castzero, cast=int),
    "ppm": partial(castzero, cast=float),
    "score": partial(castzero, cast=float),
    "ev": partial(castzero, cast=float),
    "num": partial(castzero, cast=int),
    "peptide": partial(castzero, cast=str),
    "fraction": partial(castzero, cast=str),
    "id": partial(castzero, cast=str),
    "rank": partial(castzero, cast=int)
}


# HELPERS
# -------


def forrunning(iterable, fun):
    '''Custom for loop with a caveat to break when a given the fun is False'''

    if not isinstance(iterable, types.GeneratorType):
        iterable = iter(iterable)
    try:
        while fun():
            yield next(iterable)
    except StopIteration:
        pass


# OBJECTS
# -------


@logger.init('matched', 'DEBUG')
class Truncated(base.BaseObject):
    '''Checks whether the CSV data was truncated while saving'''

    def __init__(self, engine):
        super(Truncated, self).__init__()

        self.query = engine.defaults.getflatquery()

    @logger.call('matched', 'debug')
    def __call__(self, csvrow):
        '''Checks for truncated entires in the last row'''

        if csvrow is not None:
            columns = []
            for column in self.query:
                if not any(skip in column.lower() for skip in {'mod', 'name'}):
                    columns.append(column)

            # missing -> eval True, since some data can be missing
            nulls = [i for i in columns if not csvrow.get(i, True)]
            if nulls:
                self.stop()

    #     PUBLIC

    def stop(self):
        '''Stop execution of the worker thread and emit an error code'''

        source = self.app.discovererthread
        source.isrunning = False
        source.error.emit(exception.CODES['016'], Exception)


@logger.init('matched', 'DEBUG')
class CSVUtils(base.BaseObject):
    '''Provides methods for analyzing structured, delimited text files'''

    # BREAK
    # -----
    isrunning = True

    def __init__(self, row):
        super(CSVUtils, self).__init__()

        self.row = row
        self.engine = row.engines['matched']
        self.process = PROCESS.copy()
        self.query = self.engine.defaults.getquery()

        self.truncated = Truncated(self.engine)

    @logger.call('matched', 'debug')
    def __call__(self):
        '''
        Processes all the columns besides post-translational modifications,
        which requires more intelligent parsing.
        '''

        csvrow = None
        fun = partial(op.attrgetter("isrunning"), self)
        for csvrow in forrunning(self.reader, fun):
            for key, headers in self.query.items():

                conversion = self.process[key]
                value = self.getvalue(csvrow, headers)
                value = self._convertvalue(conversion, value)

                if value is not None:
                    self.row.data['matched'][key].append(value)

        self.truncated(csvrow)

    #     SETTERS

    def set_reader(self, fileobj):
        '''Sets a reader for the CSV object from a file object'''

        delimiter = self.engine.defaults.delimiter
        self.reader = csv.DictReader(fileobj, delimiter=delimiter)

    #    GETTERS

    def getvalue(self, row, keys):
        '''
        Returns the value for processing from the row, using the nested
        nature of the keys.
        '''

        for key in keys:
            if all(i in row for i in key):
                return [row[i] for i in key]

    #     HELPERS

    def _convertvalue(self, conversion, value):
        '''Converts a given value if possible, and raises an error otherwise'''

        try:
            if value is not None:
                return conversion(value)
        except (TypeError, ValueError, AssertionError) as error:
            self._checkvalue(value, error)

    def _checkvalue(self, value, error):
        '''Checks to ensure data integrity within the given column values'''

        # Data conversion is O(n)+ by default, so best solution
        source = self.app.discovererthread
        source.isrunning = self.isrunning = False
        if value == '':
            source.error.emit(exception.CODES['016'], error)
        else:
            source.error.emit(exception.CODES['017'], error)
