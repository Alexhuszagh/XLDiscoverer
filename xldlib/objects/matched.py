'''
    Objects/matched
    _______________

    Shared objects to facilitate matched scans parsing and data
    processing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import operator as op
import os

from collections import defaultdict, namedtuple

import six

import tables as tb

from xldlib.chemical import proteins
from xldlib.general import mapping, number, sequence
from xldlib.onstart.main import APP
from xldlib.resources import paths
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, serialization

from . import mappedfile


# OBJECTS
# -------

Termini = namedtuple("Termini", "start end nterm cterm")


# MODIFICATIONS
# -------------


@serialization.register('PositionDict')
class PositionDict(defaultdict):
    '''
    Flattened, inverse representation of a modification with
    {position: name} pairs rather than {name: position}
    '''

    def __init__(self, factory=list, *args, **kwds):
        super(PositionDict, self).__init__(factory, *args, **kwds)

    #      MAGIC

    @serialization.tojson
    def __json__(self):
        return dict(self)

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(list, data)

    #     PUBLIC

    def concatenate(self, delimiter='+'):
        '''Joins the position-grouped names with a delimiter'''

        values = {k: delimiter.join(v) for k, v in self.items()}
        return PositionDict(list, values)


@serialization.register('ModificationDict')
class ModificationDict(defaultdict):
    '''Flattened representation of a modification'''

    def __init__(self, factory=list, *args, **kwds):
        super(ModificationDict, self).__init__(factory, *args, **kwds)

    #      MAGIC

    @serialization.tojson
    def __json__(self):
        return dict(self)

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(list, data)

    @classmethod
    def frommodification(cls, modification):
        '''Flattens the Modification dict'''

        inst = cls()
        items = [modification['certain']]
        if modification['uncertain']:
            items.append(modification['uncertain'][0])

        for item in items:
            for name, positions in item.items():
                inst[name] += positions

        return inst

    #     PUBLIC

    def intersect(self, other):
        return set(self) & set(other)

    def totuples(self):
        '''Yields an iterator with (name, position) pairs'''

        for name, positions in self.items():
            for position in positions:
                yield (name, position)

    def byposition(self, standardize=None):
        '''Organizes the modifications by position rather than name'''

        generator = self.totuples()
        if standardize is not None:
            generator = self.standardize(standardize)

        positions = PositionDict()
        for name, position in generator:
            positions[position].append(name)
        return positions

    def concatenate(self, standardize=None, append=True):
        '''Joins modifications at the same position with a delimiter'''

        concatenated = ModificationDict()
        positions = self.byposition(standardize)
        for position, name in positions.concatenate().items():
            if append:
                concatenated[name].append(position)
            else:
                concatenated[name] = position
        return concatenated

    def standardize(self, termini):
        '''
        Formats the terminal modifications to standardize them prior to
        modification concatenation, preventing "@N-Term" and "@1" from
        producing different positions within the sequence.

            -> [('Oxidation', 'nterm'), ('Acetyl' 'nterm')]
        '''

        termini = self._terminichecker(termini)
        positions = list(self.totuples())

        nterm = any(i[1] == termini.nterm for i in positions)
        cterm = any(i[1] == termini.cterm for i in positions)

        for name, pos in positions:
            if pos == termini.nterm or (pos == termini.start and nterm):
                yield (name, termini.nterm)
            elif pos == termini.cterm or (pos == termini.end and cterm):
                yield (name, termini.cterm)
            else:
                yield (name, pos)

    #     HELPERS

    def _terminichecker(self, termini):
        '''Checks the a proper termini object or suitable one was passed'''

        if isinstance(termini, Termini):
            return termini
        elif isinstance(termini, (list, tuple)) and len(termini) == 4:
            return Termini(*termini)
        else:
            raise TypeError("Unsuitable object passed as a Termini instance")



MODIFICATION_TEMPLATE = {
    'certain': ModificationDict(),
    'uncertain': sequence.DefaultList(ModificationDict),
    'neutralloss': number.MutableNumber(0.)
}



@mapping.serializable('MatchedModification')
class Modification(dict):
    '''Method definitions and storage for post-translation modifications'''

    #      MAGIC

    def __bool__(self, keys=('certain', 'uncertain')):
        '''bool(m) -> True'''

        return any(self[i] for i in keys)

    def __nonzero__(self):
        '''__bool__ for Python2.x'''

        return self.__bool__()

    #  CLASS METHODS

    @classmethod
    def new(cls):
        return cls(copy.deepcopy(MODIFICATION_TEMPLATE))

    #     PUBLIC

    def unpack(self):
        return ModificationDict.frommodification(self)

    def intersect(self, other):
        return self.unpack().intersect(other)

    def totuples(self):
        return self.unpack().totuples()

    def byposition(self):
        return self.unpack().byposition()

    def concatenate(self):
        '''Joins modifications at the same position with a delimiter'''

        concatenated = Modification()
        concatenated['neutralloss'] = self['neutralloss']
        concatenated['certain'] = self['certain'].concatenate()
        concatenated['uncertain'] = uncertain = []

        for item in self['uncertain']:
            uncertain.append(item.concatenate())

        return concatenated

# SCAN
# ----


@logger.init('matched', 'DEBUG')
@mapping.serializable('MatchedScan')
class Scan(dict):
    '''
    Scan object for pepXML and similar formats which follow a scan-
    based with hit hierarchy.
    '''

    precision = 4

    def __init__(self, **kwds):
        kwds.setdefault('hits', [])
        super(Scan, self).__init__(**kwds)

    #    PROPERTIES

    @property
    def include_all(self):
        return defaults.DEFAULTS['all_search_hits']

    @property
    def hit_filter(self):
        key = defaults.DEFAULTS['best_hit_key']
        return getattr(self, "_filter_" + key.lower())

    #     PUBLIC

    def set_hit(self, rank, **kwds):
        '''Initializes a set of hit'''

        hit = {
            'rank': rank,
            'modifications': Modification.new()
        }
        self['hits'].append(hit)

        return hit

    def torow(self, hit):
        '''Processes the scan data to row'''

        row = hit.copy()
        row.update(self)

        return row

    def hits(self):
        '''Returns either the best hit, or all the hits'''

        hits = self.pop('hits', [])
        if self.include_all or not hits:
            return hits
        else:
            return self.hit_filter(hits)

    #    NON-PUBLIC

    def _filter_rank(self, hits, rank=1):
        '''Filter search hits by rank, return all items <= rank'''

        return [i for i in hits if i['rank'] <= rank]

    def _filter_score(self, hits):
        '''Filter search hits by score, return the best score'''

        return max(hits, key=op.itemgetter('score'))


# TEMPLATES
# ---------


NEWFILE = {
    'matched': defaultdict(list),
    'crosslinks': [],
    'singles': [],
    'spreadsheet': defaultdict(list),
    'attrs': {
        'engines': {}
    }
}

DATA = {
    'attrs': {
        'search': None,
        'fraction': None,
        'project': None,
        'ms1': None,
        'scans': None,
        'precursor': None,
        'product': None,
        'matched': None,
    },
    'root': {
        'files': []
    }
}

SCAN_MODES = tb.Enum([
    'null',
    'spectra',
    'matched'
])


# DATA
# ----

SOURCE_ATTRIBUTES = (
    'quantitative',
    'fingerprinting',
    'reporterions'
)

PRECURSOR_KEYS = (
    'precursor_num',
    'precursor_rt',
    'precursor_mz',
    'precursor_z'
)


@logger.init('matched', 'DEBUG')
@mapping.serializable('DataTable')
class DataTable(dict):
    '''Matched datatable interface to XL Discoverer'''

    def __init__(self, data=None, **attrs):
        if data is None:
            data = copy.deepcopy(NEWFILE)
        super(DataTable, self).__init__(data)

        for key, value in attrs.items():
            self['attrs'][key] = value

        for key, path in attrs.get('files', {}).items():
            self['attrs'][key] = os.path.basename(path)

    #   PROPERTIES

    @property
    def protease(self):
        '''Returns the protease if defined or undefined'''

        enzyme = self['attrs'].get('enzyme')
        if enzyme is not None:
            return proteins.ProteolyticEnzyme(enzyme)
        else:
            logger.warn("Protease not specified in matched peptides")

    #     PUBLIC

    def newscan(self, scan):
        '''Appends all search hit data from the scans'''

        for hit in scan.hits():
            row = scan.torow(hit)
            self.setfromdict(row)

    def setnull(self, keys=PRECURSOR_KEYS, blank=None):
        '''Sets a default placeholder (None) when no item is found'''

        length = len(self['matched']['id'])
        for key in keys:
            self['matched'].setdefault(key, [blank]*length)

    def setfromdict(self, mapping, index=None):
        '''Appends the data from a mapping structure to the given index'''

        for key, value in mapping.items():
            if index is None:
                self['matched'][key].append(value)
            else:
                self['matched'][key][index] = value

        if index is None:
            # need to make sure no uneven addition, all columns equal
            fields = set(self['matched'])
            for key in fields - set(mapping):
                self['matched'][key].append(float('nan'))

    def getattr(self, attr):
        return self['attrs'].get(attr)

    def setattr(self, attr, value):
        self['attrs'][attr] = value

    #     ROWS

    def findrows(self, column, lookup):
        '''Returns the indexes of values in the lookup table from the column'''

        for index, value in enumerate(self['matched'][column]):
            if value in lookup:
                yield index

    def iterrows(self, columns=None, asdict=False):
        '''Returns an iterator for all items within the table'''

        if columns is None:
            columns = list(self['matched'])

        for row in range(len(self['matched']['id'])):
            yield self.getrow(row, columns, asdict)

    def getrow(self, row, columns=None, asdict=False):
        '''Extracts given columns from a single row in the table'''

        if columns is None:
            columns = list(self['matched'])

        if asdict:
            return {i: self['matched'][i][row] for i in columns}
        else:
            return [self['matched'][i][row] for i in columns]

    def getrows(self, rows, columns=None, asdict=False):
        '''Extracts given columns for each row in the table'''

        if columns is None:
            columns = list(self['matched'])

        return [self.getrow(i, columns, asdict) for i in rows]

    def deleterow(self, row):
        '''Deletes a row from the DataTable'''

        for column in self['matched']:
            del self['matched'][column][row]

    def deleterows(self, rows):
        for row in rows:
            self.deleterow(row)

    #   COLUMNS

    def getcolumn(self, rows, column, asdict=False):
        '''Returns all rows for the given column'''

        if isinstance(column, six.string_types):
            for row in rows:
                yield self['matched'][column][row]

        elif hasattr(column, "__iter__"):
            for row in rows:
                if asdict:
                    yield {i: self['matched'][i][row] for i in column}
                else:
                    yield [self['matched'][i][row] for i in column]

    #   GROUPING

    def groupby(self, column='num', indexes=None, fields=None):
        '''Groups values in '''

        if indexes is None:
            indexes = range(len(self['matched']['id']))

        grouped = defaultdict(list)
        for index in indexes:
            key = self['matched'][column][index]
            if fields is None:
                grouped[key].append(index)
            else:
                values = tuple(self['matched'][i][index] for i in fields)
                grouped[key].append((index,) + values)

        return grouped

    def columnmax(self, column, fields):
        return self.columnkey(column, fields, max)

    def columnmin(self, column, fields):
        return self.columnkey(column, fields, min)

    def columnkey(self, column, fields, key):
        '''Returns the best from getter for a given column for each field'''

        grouped = self.groupby(column, fields=fields)
        for index in range(len(fields)):
            yield {k: key(i[index+1] for i in v) for k, v in grouped.items()}


# FILE
# ----


@serialization.register('MatchedFile')
class File(mappedfile.File):
    '''Provides a convenient table and crosslink interface to XL Discoverer'''

    #     MAGIC

    def __iter__(self):
        return iter(self.data['root']['files'])

    def __len__(self):
        return len(self.data['root']['files'])

    def __getitem__(self, index):
        return self.data['root']['files'][index]

    def __delitem__(self, index):
        del self.data['attrs']['engines'][index]
        del self.data['root']['files'][index]

    #     PUBLIC

    def append(self, table):
        self.data['root']['files'].append(table)

    def newtable(self, files):
        table = DataTable(files=files)
        self.append(table)
        return table

    def delete(self, index):
        del self.data['root']['files'][index]

    #     HELPERS

    @staticmethod
    def _new(blank):
        '''Defines a new, template data structure'''

        data = copy.deepcopy(DATA)

        if not blank:
            source = APP.discovererthread

            for attr in SOURCE_ATTRIBUTES:
                data['attrs'][attr] = getattr(source, attr)

            for key, value in source.parameters.items():
                if key not in {'search', 'spectra'}:
                    data['attrs'][key] = value

        return data

    @staticmethod
    def _newpath():
        return paths.FILES['matched']
