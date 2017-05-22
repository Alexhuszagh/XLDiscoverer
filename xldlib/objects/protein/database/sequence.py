'''
    Objects/Protein/sequence
    ________________________

    Dataset to store protein sequences and UniProt ID numbers

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    >>> db = ProteinTable()
    >>> db.new()
'''

# load modules
import shutil

import tables as tb

from xldlib.objects import sqlite
from xldlib.resources import paths
from xldlib.utils import logger

# load objects/functions
from collections import defaultdict


# ENUMS
# -----

LimitedDatabase = tb.Enum([
    'None',
    'Mild',
    'Strict'
])


# HELPERS
# -------


def get_path(path):
    '''Returns a valid path object, which defaults to the current db'''

    if path is None:
        path = paths.DYNAMIC['current_proteins']
    return path


# CONSTRUCTORS
# ------------


PROTEIN_CONSTRUCTOR = '''CREATE TABLE [{table}] (
    [IntegerID] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [Name] [text] NULL,
    [UniProtID] [text] NULL,
    [Mnemonic] [text] NULL,
    [Sequence] [text] NULL,
    [Length] [int] NULL,
    [MolecularWeight] [double] NULL)'''


NAME_CONSTRUCTOR = '''CREATE TABLE [{table}] (
    [IntegerID] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [Name] [text] NULL,
    [UniProtID] [text] NULL)'''

TAXONOMY_CONSTRUCTOR = '''CREATE TABLE [{table}] (
    [IntegerID] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [TaxonomyID] INTEGER NULL,
    [Name] [text] NULL)
'''

PARAMETER_CONSTRUCTION = '''CREATE TABLE [{table}] (
    [IntegerID] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [ParameterName] [text] NOT NULL,
    [ParameterValue] [text] NULL)
'''


# TABLES
# ------


PROTEIN_TABLES = [
    'Proteins'
]

NAME_TABLES = [
    'Blacklist',
    'Greylist',
    'Named',
    'Decoys',
    'Depricated'
]

TAXONOMY_TABLES = [
    'Taxonomy'
]

PARAMETER_TABLES = [
    'SearchParameters'
]

ATTR_TO_FIELD = {
    'id': 'UniProtID',
    'mnemonic': 'Mnemonic',
}

TABLES = [
    (PROTEIN_CONSTRUCTOR, PROTEIN_TABLES),
    (NAME_CONSTRUCTOR, NAME_TABLES),
    (TAXONOMY_CONSTRUCTOR, TAXONOMY_TABLES),
    (PARAMETER_CONSTRUCTION, PARAMETER_TABLES),
]


# OBJECTS
# -------


@logger.init('database', 'DEBUG')
class ProteinTable(sqlite.SqlFile):
    '''Definitions for storing protein references with sequences'''

    def __init__(self, **kwds):
        super(ProteinTable, self).__init__()

        if kwds.get('open'):
            self.open(kwds.get('path'))
        elif kwds.get('tryopen'):
            self.tryopen(kwds.get('path'))
        elif kwds.get('new'):
            self.new(kwds.get('path'))

        if kwds.get('set_mapping'):
            self.set_mapping()

    #     PUBLIC

    @logger.call('database', 'debug')
    def new(self, path=None, limited=LimitedDatabase['None']):
        '''Create new dataset'''

        path = get_path(path)
        self._new(path)
        self.limited = limited

        for constructor, tables in TABLES:
            for name in tables:
                self.execute(constructor.format(table=name))
        self.set_limited(limited)

    @logger.call('database', 'debug')
    def open(self, path=None):
        '''Initialize dataset from path'''

        path = get_path(path)
        self._open(path)
        self.limited = self.get_limited()

    @logger.call('database', 'debug')
    def tryopen(self, path=None):
        '''Tries to open the dataset, if not, creates a new one from scratch'''

        path = get_path(path)
        try:
            self.open(path)
        except (OSError, IOError):
            self.new(path)

    def saveas(self, path):
        shutil.copy2(self.path, path)

    #    SETTERS

    def set_limited(self, limited):
        '''Stores the limited database status for the SQL table'''

        self.execute(('''INSERT INTO SearchParameters
            (ParameterName, ParameterValue)
            VALUES (?, ?);''', ('LimitedDatabase', limited)))

    def set_mapping(self):
        '''Sets the mapping interface for the current databases'''

        self.mapping = defaultdict(dict)
        for name in PROTEIN_TABLES:
            for attr in ('id', 'mnemonic'):
                self.set_ids(name, attr)

        for name in NAME_TABLES:
            self.set_ids(name, 'id')

    def set_ids(self, name, attr):
        '''Sets the name mapping for the given IDs for quick lookups'''

        records = self.fetchall("SELECT * FROM {};".format(name))
        field = ATTR_TO_FIELD[attr]
        for index, record in enumerate(records):
            value = record.value(field)
            self.mapping[name.lower()][value] = index

    #    GETTERS

    def get_limited(self, as_string=False):
        '''Gets the limited database status for the SQL table'''

        value = self.fetchone(('''SELECT ParameterValue
            FROM SearchParameters
            WHERE ParameterName=?;''', ('LimitedDatabase',)))
        limited = int(value[0])

        if as_string:
            return LimitedDatabase(limited)
        else:
            return limited

    def get_lookup(self, table, column):
        '''
        Returns a spectral lookup table with each uniprot ID mapped
        to another value.
        '''

        sqlquery = "SELECT UniProtID, {0} FROM {1}".format(column, table)
        return {i.value(0): i.value(1) for i in self.fetchiter(sqlquery)}
