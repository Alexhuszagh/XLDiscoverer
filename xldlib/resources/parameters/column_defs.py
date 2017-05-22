'''
    Resources/Parameters/column_defs
    ________________________________

    Spreadsheet columns for Open Office reports.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import os
import six

from namedlist import FACTORY, namedlist

import tables as tb

from xldlib.definitions import re, ZIP
from xldlib.general import mapping, sequence
from xldlib.resources import paths
from xldlib.utils import serialization


# CONSTANTS
# ---------

INT_FORMATTING = {'num_format': "0"}
FLOAT_FORMATTING = {'num_format': "#.###"}
FLOAT1_FORMATTING = {'num_format': "#.0"}
FLOAT2_FORMATTING = {'num_format': "#.##"}
SCI1_FORMATTING = {'num_format': "0.0E+#"}
SCI2_FORMATTING = {'num_format': "0.00E+#"}

# DATA
# ----

MS1COLUMNS = [
    "Cross-Linker",
    "Peptide",
    "MS2 m/z",
    "Protein Mods",
    "Area",
    "Intensity",
    "Min Window",
    "Max Window",
    "Included Charges",
    "Integrated PPM",
    "XIC Fit Score",
    "Linear w/ Mods"
]
MS1LOOKUP = set(MS1COLUMNS)

# PATHS
# -----

COLUMNSPATH = os.path.join(paths.DIRS['data'], 'columns.json')


# ENUMS
# -----

REPORTNAMES = tb.Enum([
    'report',
    'best_peptide',
    'best_peptide_file',
    'comparative',
    'comparative_named',
    'quantitative',
    'quantitative_comparative',
    'skyline',
    'overall',
    'ratiotable',
])

BLOCKTYPES = tb.Enum([
    'static',
    'sequential',
    'clustered',
    'unused',
])


# OBJECTS
# -------

@sequence.serializable("SeriesColumns")
class SeriesColumns(namedlist("SeriesColumns", "type columns")):
    '''Holds a series of uniformly labeled columns'''


@sequence.serializable("ColumnBlock")
class Block(namedlist("Block" , "type columns")):
    '''Holds a series of sequential columns'''

    def getseries(self):
        '''Returns a series of a uniformly-labeled column types'''

        series = []
        labeled = None

        for column in self.columns:
            islabeled = column.key in MS1LOOKUP
            if labeled != islabeled:
                labeled = islabeled
                subseries = SeriesColumns(labeled, [column])
                series.append(subseries)

            else:
                subseries.columns.append(column)
        return series


@mapping.serializable("ColumnsDict")
class ColumnsDict(dict):
    '''Custom __getitem__ that removes suffixes'''

    # REGEXES
    # -------
    suffix = re.compile(r'^.* (?:[A-Z0-9])$')
    whitespace = re.compile(r'\s+')

    #      MAGIC

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''CD[k] -> v'''

        key = self._keychecker(key)
        return dict_getitem(self, key)

    #     HELPERS

    def _keychecker(self, item):
        '''Returns the suffix-less key'''

        if isinstance(item, six.string_types):
            return self._stringchecker(item)
        elif isinstance(item, (list, tuple)):
            return self._sequencechecker(item)

    def _stringchecker(self, item):
        '''Returns the suffix-less key from a string column'''

        if self.suffix.match(item):
            return item[:-2]
        return item

    def _sequencechecker(self, item):
        '''Returns the suffix-less key from a column sequence'''

        # comparative has null string columns in row 1, while quantitative
        # has null or isotope columns in row 0
        string = [i for i in item if self.whitespace.sub("", i)][-1]
        if self.suffix.match(string):
            return string[:-2]
        return string


@serialization.register("OrderedColumns")
class OrderedColumns(list):
    '''Definitions for ordered columns'''

    @serialization.tojson
    def __json__(self):
        return list(self)

    @classmethod
    def loadjson(cls, data):
        return cls(data)

    def getlabeled(self, labels, series):
        '''Adds isotope labels to the column series'''

        if not series.type:
            # no labels, use a generic ' ' header
            for column in self:
                yield (' ', column)
        else:
            # labeled
            for label in labels:
                for column in self:
                    yield (label, column)


@sequence.serializable("ColumnReport")
class Report(namedlist("Report" , [
    'name',
    ('digit', False),
    ('blocks', ()),
    ('editable', True),
    ('other', None)
])):
    '''Subclass with default arguments and dynamic collapsing to a list'''

    #  PUBLIC FUNCTIONS

    def asdict(self):
        '''Returns a dict representation with a name: column object'''

        columns = ColumnsDict()
        for block in self.blocks:
            for column in block.columns:
                columns[column.key] = column

        return columns

    #     GETTERS

    def getsuffix(self, index):
        '''Returns the suffix from an index'''

        if self.digit:
            return ' ' + str(index+1)
        else:
            return ' ' + chr(index + ord('A'))

    def _getblock(self, block, count, fun, force_suffix=False):
        '''Returns the columns from a singular block'''

        if block.type == BLOCKTYPES['unused']:
            # to avoid next condition's potential fallthrough
            pass
        elif (block.type == BLOCKTYPES['static'] or
            (count == 1 and not force_suffix)):
            for column in block.columns:
                yield fun(column)
        elif block.type == BLOCKTYPES['sequential']:
            for index in range(count):
                suffix = self.getsuffix(index)
                for column in block.columns:
                    yield fun(column) + suffix
        elif block.type == BLOCKTYPES['clustered']:
            for column in block.columns:
                for index in range(count):
                    yield fun(column) + self.getsuffix(index)

    def getblock(self, *args, **kwds):
            return OrderedColumns(self._getblock(*args, **kwds))

    def getordered(self, count, fun=op.attrgetter('key'), **kwds):
        '''Returns the columns ordered in a list with various suffixes'''

        columns = OrderedColumns()
        for block in self.blocks:
            columns.extend(self._getblock(block, count, fun, **kwds))
        return columns

    def getrename(self, count):
         '''Returns a rename dictionary with each original name to newname'''

         original = self.getordered(count)
         new = self.getordered(count, fun=op.attrgetter('name'))
         return {k: v for k, v in ZIP(original, new) if k != v}

    def getresize(self, count):
        '''Returns the resiable columns'''

        original = self.getordered(count)
        new = self.getordered(count, force_suffix=True)
        return {k: v for k, v in ZIP(original, new) if k != v}


@sequence.serializable("SpreadsheetColumn")
class Column(namedlist("Column" , [
    'key',
    ('tag', None),
    ('size', None),
    ('formatting', FACTORY(dict))
])):
    '''Definitions for a spreadsheet column, including key, name and style'''

    @property
    def name(self):
        return self.tag or self.key



@serialization.register("ColumnStorage")
class ColumnStorage(mapping.Configurations):
    '''Column storage definitions'''

    # TODO: implement methods for block addition/removal

    #      MAGIC

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''self[k] -> v'''

        key = self._keychecker(key)
        return dict_getitem(self, key)

    #     HELPERS

    def insert_block(self, type_, *columns):
        pass

    def remove_block(self, index):
        pass

    def _keychecker(self, item):
        '''Returns the enum for the key'''

        if isinstance(item, six.string_types):
            return REPORTNAMES[item]
        return item

# DATA
# ----


COLUMNS = ColumnStorage(COLUMNSPATH, [
    (REPORTNAMES['report'], Report(name='{}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column('Subunit',
                        size=15),
                    Column('XL',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['clustered'],
                columns=[
                    Column('Subunit Name',
                        size=15),
                    Column('Common/Gene Name',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('MS2 PPM',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 PPM Corrected',
                        size=25,
                        formatting=FLOAT_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("MS3 m/z",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 z",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("DB Peptide",
                        size=25),
                    Column("Protein Mods",
                        size=25),
                    Column("MS3 PPM",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 Score",
                        size=15,
                        formatting=FLOAT1_FORMATTING),
                    Column("MS3 EV",
                        size=15,
                        formatting=SCI1_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Ambiguous",
                        size=15),
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("Counts Info",
                        size=15),
                    Column("Counts Unique Info",
                        size=30),
                    Column("xiNet",
                        size=40),
                    Column("{reporterion} Ratios",
                        size=40),
                    Column("{reporterion} m/z",
                        size=40),
                    Column("{reporterion} Intensity",
                        size=40),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Cross-Linker"),
                    Column("Cross-Link Number"),
                    Column("Project Name"),
                    Column("MS Scans Name"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Product Scan"),
                    Column("Search Rank"),
                    Column("Runtime"),
                    Column("Peptide"),
                    Column("Start"),
                    Column("Missing Mass"),
                    Column("Double"),
                    Column("Intersubunit"),
                    Column("Intrasubunit"),
                    Column("Deadend"),
                    Column("Single"),
                    Column("Intralink"),
                ])
        ])),
    (REPORTNAMES['best_peptide'], Report(name='Best IDs {} -- All',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column('Subunit',
                        size=15),
                    Column('XL',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['clustered'],
                columns=[
                    Column('Subunit Name',
                        size=15),
                    Column('Common/Gene Name',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('MS2 PPM',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 PPM Corrected',
                        size=25,
                        formatting=FLOAT_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("MS3 m/z",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 z",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("DB Peptide",
                        size=25),
                    Column("Protein Mods",
                        size=25),
                    Column("MS3 PPM",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 Score",
                        size=15,
                        formatting=FLOAT1_FORMATTING),
                    Column("MS3 EV",
                        size=15,
                        formatting=SCI1_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Ambiguous",
                        size=15),
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("xiNet",
                        size=40),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Cross-Linker"),
                    Column("Cross-Link Number"),
                    Column("Project Name"),
                    Column("MS Scans Name"),
                    Column("Product Scan"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Search Rank"),
                    Column("Peptide"),
                    Column("Start"),
                    Column("Missing Mass"),
                    Column("Double"),
                    Column("Intersubunit"),
                    Column("Intrasubunit"),
                    Column("Deadend"),
                    Column("Single"),
                    Column("Intralink"),
                    Column("Counts Info"),
                    Column("Counts Unique Info"),
                    Column("{reporterion} Ratios"),
                    Column("{reporterion} m/z"),
                    Column("{reporterion} Intensity")
                ])
        ])),
    (REPORTNAMES['best_peptide_file'], Report(name='Best IDs {} -- File',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column('Subunit',
                        size=15),
                    Column('XL',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['clustered'],
                columns=[
                    Column('Subunit Name',
                        size=15),
                    Column('Common/Gene Name',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('MS2 PPM',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 PPM Corrected',
                        size=25,
                        formatting=FLOAT_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("MS3 m/z",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 z",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("DB Peptide",
                        size=25),
                    Column("Protein Mods",
                        size=25),
                    Column("MS3 PPM",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 Score",
                        size=15,
                        formatting=FLOAT1_FORMATTING),
                    Column("MS3 EV",
                        size=15,
                        formatting=SCI1_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Ambiguous",
                        size=15),
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("xiNet",
                        size=40),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Cross-Linker"),
                    Column("Cross-Link Number"),
                    Column("Project Name"),
                    Column("MS Scans Name"),
                    Column("Product Scan"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Search Rank"),
                    Column("Peptide"),
                    Column("Start"),
                    Column("Missing Mass"),
                    Column("Double"),
                    Column("Intersubunit"),
                    Column("Intrasubunit"),
                    Column("Deadend"),
                    Column("Single"),
                    Column("Intralink"),
                    Column("Counts Info"),
                    Column("Counts Unique Info"),
                    Column("{reporterion} Ratios"),
                    Column("{reporterion} m/z"),
                    Column("{reporterion} Intensity")
                ])
        ])),
    (REPORTNAMES['comparative'], Report(name='Comparative {}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("Count",
                        size=10),
                    Column("Sum",
                        size=10),
                ])
        ],
        editable=False,
        # order -- ['File', 'Crosslinker']
        other={'order': 'File',
            # counts -- ['Unique', 'Redundant']
            'counts': 'Redundant'})),
    (REPORTNAMES['comparative_named'], Report(name='Named Comparative {}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("Count",
                        size=10),
                    Column("Sum",
                        size=10),
                ])
        ],
        editable=False,
        # order -- ['File', 'Crosslinker']
        other={'order': 'File',
            # counts -- ['Unique', 'Redundant']
            'counts': 'Redundant'})),
    (REPORTNAMES['quantitative'], Report(name='Quantitative {}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column('Subunit',
                        size=15),
                    Column('XL',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['clustered'],
                columns=[
                    Column('Subunit Name',
                        size=15),
                    Column('Common/Gene Name',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("MS1 Scan",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("MS1 RT",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("Product Scan",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('MS2 PPM',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 PPM Corrected',
                        size=25,
                        formatting=FLOAT_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("MS3 m/z",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 z",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("DB Peptide",
                        size=25),
                    Column("Protein Mods",
                        size=25),
                    Column("MS3 PPM",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 Score",
                        size=15,
                        formatting=FLOAT1_FORMATTING),
                    Column("MS3 EV",
                        size=15,
                        formatting=SCI1_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Ambiguous",
                        size=15),
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("xiNet",
                        size=40),
                    Column('Area',
                        size=15,
                        formatting=SCI2_FORMATTING),
                    Column("Intensity",
                        size=20,
                        formatting=SCI2_FORMATTING),
                    Column("Min Window",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("Max Window",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("Included Charges",
                        size=20),
                    Column("Integrated PPM",
                        size=20,
                        formatting=FLOAT_FORMATTING),
                    Column("XIC Fit Score",
                        size=20,
                        formatting=FLOAT2_FORMATTING),
                    Column("Ratio Area",
                        size=20),
                    Column("Ratio Intensity",
                        size=20),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Cross-Linker"),
                    Column("Cross-Link Number"),
                    Column("Project Name"),
                    Column("MS1 Scans Name"),
                    Column("MS Scans Name"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Runtime"),
                    Column("Search Rank"),
                    Column("Peptide"),
                    Column("Start"),
                    Column("Missing Mass"),
                    Column("Double"),
                    Column("Intersubunit"),
                    Column("Intrasubunit"),
                    Column("Deadend"),
                    Column("Single"),
                    Column("Intralink"),
                    Column("Counts Info"),
                    Column("Counts Unique Info"),
                    Column("XiQ"),
                    Column("{reporterion} Ratios"),
                    Column("{reporterion} m/z"),
                    Column("{reporterion} Intensity")
                ])
        ])),
    (REPORTNAMES['quantitative_comparative'], Report(
        name='QC {}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("Count",
                        size=10),
                    Column("Sum",
                        size=10),
                ])
        ],
        editable=False,
        # order -- ['File', 'Crosslinker']
        other={'order': 'File',
            # counts -- ['Unique', 'Redundant']
            'counts': 'Unique'})),
    (REPORTNAMES['skyline'], Report(name='Skyline',
        digit=True,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('Runtime',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("Common/Gene Name",
                        tag='Protein',
                        size=15),
                    Column("XL",
                        tag='Residue',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column(" ",
                        size=5),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("DB Peptide",
                        tag='Peptide',
                        size=25),
                    Column("Protein Mods",
                        tag='Modification',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("  ",
                        size=5),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Linear",
                        size=25),
                    Column("Linear w/ Mods",
                        size=30),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Project Name"),
                    Column("MS Scans Name"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Search Rank"),
                    Column("Double"),
                    Column("Intersubunit"),
                    Column("Intrasubunit"),
                    Column("Deadend"),
                    Column("Single"),
                    Column("Intralink"),
                    Column("MS3 m/z"),
                    Column("MS3 z"),
                    Column("Peptide"),
                    Column("MS3 PPM"),
                    Column("MS3 Score"),
                    Column("MS3 EV"),
                    Column("Subunit"),
                    Column("Product Scan"),
                    Column("Subunit Name"),
                    Column("MS2 PPM"),
                    Column("MS2 PPM Corrected"),
                    Column("Start"),
                    Column("Ambiguous"),
                    Column("Subunit Names"),
                    Column("Missing Mass"),
                    Column("Linkage Info"),
                    Column("Counts Info"),
                    Column("Counts Unique Info"),
                    Column("xiNet"),
                    Column("{reporterion} Ratios"),
                    Column("{reporterion} m/z"),
                    Column("{reporterion} Intensity")
                ]),
        ])),
    (REPORTNAMES['overall'], Report(name='General Report',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Matched Output Name',
                        size=15),
                    Column('Search Name',
                        size=25),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column('Common/Gene Name',
                        size=15),
                ]),
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column('Precursor Scan',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column('Precursor RT',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 m/z',
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column('MS2 z',
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("Double",
                        size=15),
                    Column("Intersubunit",
                        size=15),
                    Column("Intrasubunit",
                        size=15),
                    Column("Deadend",
                        size=15),
                    Column("Single",
                        size=15),
                    Column("Intralink",
                        size=15),
                ]),
            Block(type=BLOCKTYPES['sequential'],
                columns=[
                    Column("MS3 m/z",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 z",
                        size=15,
                        formatting=INT_FORMATTING),
                    Column("DB Peptide",
                        size=25),
                    Column("Peptide",
                        size=25),
                    Column("Protein Mods",
                        size=25),
                    Column("MS3 PPM",
                        size=15,
                        formatting=FLOAT_FORMATTING),
                    Column("MS3 Score",
                        size=15,
                        formatting=FLOAT1_FORMATTING),
                    Column("MS3 EV",
                        size=15,
                        formatting=SCI1_FORMATTING),
                    Column("Subunit",
                        size=15),
                    Column("Subunit Name",
                        size=20),
                ]),
            Block(type=BLOCKTYPES['unused'],
                columns=[
                    Column("Project Name"),
                    Column("MS Scans Name"),
                    Column("Precursor Scans Name"),
                    Column("Product Scans Name"),
                    Column("Product Scan"),
                    Column("Runtime"),
                    Column("Search Rank"),
                    Column("MS2 PPM"),
                    Column("MS2 PPM Corrected"),
                    Column("XL"),
                    Column("Start"),
                    Column("Ambiguous"),
                    Column("Subunit Names"),
                    Column("Missing Mass"),
                    Column("Linkage Info"),
                    Column("Counts Info"),
                    Column("Counts Unique Info"),
                    Column("xiNet"),
                    Column("{reporterion} Ratios"),
                    Column("{reporterion} m/z"),
                    Column("{reporterion} Intensity")
                ]),
        ])),
    (REPORTNAMES['ratiotable'], Report(
        name='Ratios {}',
        digit=False,
        blocks=[
            Block(type=BLOCKTYPES['static'],
                columns=[
                    Column("Subunit Names",
                        size=20),
                    Column("Linkage Info",
                        size=25),
                    Column("Count",
                        size=15),
                    Column("Sum",
                        size=15)
                ])
        ],
        editable=False,
        # order -- ['File', 'Label Header']
        other={'order': 'File',
               # counts -- ['Unique', 'Redundant']
               'counts': 'Unique'})),
])
