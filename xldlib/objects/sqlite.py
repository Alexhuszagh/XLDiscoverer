'''
    Objects/sqlite
    ______________

    Wrapper definitions for SQLite2 and SQLite3 objects, using
    QtSql bindings.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    >>> f = SqlFile()
    >>> f.open(':memory:')

    >>> # check equality testing -- same file
    >>> g = f
    >>> g == f
    True

    >>> # different files
    >>> g = SqlFile()
    >>> g.open(':memory:')
    >>> g == f
    False
'''

# load modules
import os
import six

from PySide import QtSql

from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.utils.io_ import high_level


# CONSTANTS
# ---------

CONNECTION = 'protein_database'


# SETTINGS
# --------

MEMORY_QUERIES = (
    "PRAGMA page_size = 4096",
    "PRAGMA cache_size = 16384",
    "PRAGMA temp_store = MEMORY",
    "PRAGMA journal_mode = OFF",
    "PRAGMA locking_mode = EXCLUSIVE",
    "PRAGMA synchronous = OFF"
)

# HELPERS
# -------


def iterquery(query):
    '''High-level wrapper for a query to facilitate iteration'''

    while query.next():
        yield query.record()
    query.finish()


# OBJECTS
# -------


@logger.init('database', 'DEBUG')
class SqlFile(base.BaseObject):
    '''Definitions for an Sql File object wrapper'''

    def __init__(self):
        super(SqlFile, self).__init__()

        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE", CONNECTION)
        self.path = None

    #     MAGIC

    def __len__(self):
        return len(self.master())

    def __eq__(self, other):
        '''Equality implentation for SqlFiles'''

        if isinstance(other, SqlFile):
            if self.path == ':memory:':
                return id(self) == id(other)
            else:
                self.path == other.path
        return False

    def __ne__(self, other):
        return not self == other

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return isinstance(exc_val, (OSError,))

    #       I/O

    def _new(self, path):
        '''Initializes a new SQLite connection'''

        self._close()

        self.path = path
        if os.path.exists(path):
            high_level.remove_file(self.path)
        self._opendb()

    def _open(self, path):
        '''Opens an SQLite connection from file (or ":memory:")'''

        self._close()

        self.path = path
        self._opendb()

    def _opendb(self):
        '''Opens the database and sets the query object (cursor)'''

        if self.db is None:
            self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE", CONNECTION)
        self.db.setDatabaseName(self.path)
        assert self.db.open(), "Cannot establish database connection"

        for sqlquery in MEMORY_QUERIES:
            self.execute(sqlquery)

    def _close(self):
        '''Closes an open SQLite connection'''

        if self.path is not None:
            self.db.close()
            self.db = None
            self.path = None

            QtSql.QSqlDatabase.removeDatabase(CONNECTION)

    def _save(self):
        '''Commits changes to the database'''

        self.assertopen()
        self.db.commit()

    #    PUBLIC

    new = _new
    open = _open
    close = _close
    save = _save

    #    QUERIES

    def query(self):
        return QtSql.QSqlQuery(self.db.database(CONNECTION))

    def execute(self, sqlquery):
        '''Execute an SQLite query string'''

        self.assertopen()
        if isinstance(sqlquery, tuple):
            return self._bindquery(sqlquery)
        else:
            query = self.query()
            assert query.exec_(sqlquery)
            return query

    def _bindquery(self, sqlquery):
        '''Initializes a query with bound values, to avoid SQL injection'''

        statement, args = sqlquery
        query = self.query()
        query.prepare(statement)
        for arg in args:
            if isinstance(arg, tuple):
                # named or qmark (v1)
                query.bindValue(*arg)
            else:
                # qmark (v2)
                query.addBindValue(arg)
        assert query.exec_()
        return query

    #    FETCH

    def fetchone(self, query):
        '''Fetch a single object from an SQL Query'''

        if isinstance(query, (six.string_types, list, tuple)):
            query = self.execute(query)

        query.next()
        value = query.value(0)
        query.finish()
        return value

    def fetchall(self, query):
        return list(self.fetchiter(query))

    def fetchiter(self, query):
        '''Lazy evaluaution of all objects from an SQL Query'''

        if isinstance(query, (six.string_types, list, tuple)):
            query = self.execute(query)
        return iterquery(query)

    def master(self):
        query = "SELECT name from sqlite_master WHERE type='table';"
        return self.fetchall(query)

    #    COMMITS

    def commit(self):
        self.assertopen()
        self.db.commit()

    #    HELPERS

    def assertopen(self):
        assert self.db.isOpen(), "No active database connection found"
