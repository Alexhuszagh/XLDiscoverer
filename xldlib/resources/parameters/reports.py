'''
    Resources/Parameters/reports
    ____________________________

    Reports to include in the exported spreadsheets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os
import six

import tables as tb

from xldlib.general import mapping, sequence
from xldlib.resources import  paths
from xldlib.utils import serialization

from . import column_defs

# load objects/functions
from collections import defaultdict, namedtuple

# PATHS
# -----

REPORT_PATH = os.path.join(paths.DIRS['data'], 'reports.json')


# ENUMS
# -----

REPORT_TYPES = tb.Enum([
    'dependent',
    'independent'
])


DEPENDENT_REPORTS = tb.Enum([
    'overall',
    'skyline'
])

LINKNAMES = tb.Enum([
    'Standard',
    'Low Confidence',
    'Fingerprint',
    'Incomplete'
])

LINKTYPES = tb.Enum([
    'interlink',
    'intralink',
    'deadend',
    'multilink',
    'single'
])


# OBJECTS
# -------

Report = namedtuple("Report", "name sheets")
Independent = namedtuple("Independent", "linkname linktype sheet")
Dependent = namedtuple("Dependent", "sheet")


@sequence.serializable("ReportSheet")
class Sheet(namedtuple("Sheet", "title name columns "
    "type reports linkname linktype")):

    def __new__(cls, title, name, columns, type,
        reports=None, linkname=None, linktype=None):
        return super(Sheet, cls).__new__(cls, title, name, columns,
            type, reports, linkname, linktype)

    @classmethod
    def fromorder(cls, item):
        '''Initialies a new sheet from a namedtuple item'''

        column = column_defs.COLUMNS[item.sheet]

        if isinstance(item, Independent):
            report = REPORTS[item.linkname, item.linktype]
            name = column.name.format(report.name)
            return cls(name, item.sheet, column, REPORT_TYPES['independent'],
                report, item.linkname, item.linktype)

        elif isinstance(item, Dependent):
            return Sheet(column.name, item.sheet,
                column, REPORT_TYPES['dependent'])


@serialization.register("ReportStorage")
class ReportStorage(mapping.IoMapping):
    '''Parameters for reports which get converted to spreadsheets'''

    # PROTECTED
    # ---------
    __update = dict.update
    __getitem = dict.__getitem__

    # ERRORS
    # ------
    report_error = "Report object not recognized"

    def __init__(self, path, reports, order):
        super(ReportStorage, self).__init__()

        self.path = path
        self.__update(order=order, reports=defaultdict(dict))
        self.order = self.__getitem('order')
        self.reports = self.__getitem('reports')

        self.setdependent()

        for linkname in reports:
            for linktype, report in reports[linkname].items():
                self[linkname, linktype] = report

        self.ioload()

    #     MAGIC

    def __setitem__(self, key, value):
        '''RS[k] = v -> RS.reports[k] = v'''

        linkname, linktype = self._keychecker(key)
        value = self._reportchecker(value)
        self.reports[linkname][linktype] = value

        for name in DEPENDENT_REPORTS._names:
            if value.sheets.get(name, False):
                if name not in self.dependent:
                    self.order.append(Dependent(sheet=name))
                self.dependent[name].add((linkname, linktype))

    def __getitem__(self, key):
        '''RS[k] -> RS.reports[k] -> v'''

        linkname, linktype = self._keychecker(key)
        return self.reports[linkname][linktype]

    def __delitem__(self, key):
        '''del RS[k] -> del RS.reports[k]'''

        linkname, linktype = self._keychecker(key)
        value = self.reports[linkname].pop(linktype)

        for name in DEPENDENT_REPORTS._names:
            if value.sheets.get(name, False):
                self.dependent[name].remove((linkname, linktype))

                if not self.dependent[name]:
                    del self.dependent[name]
                    self.order.remove(Dependent(sheet=name))

    #     SETTERS

    def setdependent(self):
        '''Initializes the dependent reports'''

        self.dependent = defaultdict(set)
        for report in self.order:
            if isinstance(report, Dependent):
                self.dependent[report.sheet]

    #     GETTERS

    def getsheets(self):
        return [Sheet.fromorder(i) for i in self.order]

    #     HELPERS

    def update(self, *args, **kwds):
        '''
        Update configuration from an iterable in `args`, and keyword
        arguments in `kwds`
        '''

        mapping.update_checker(self, args, kwds)

        # Make progressively weaker assumptions about "other"
        other = ()
        if len(args) == 1:
            other = args[0]
        if isinstance(other, dict):
            _pairwise_iterator(self, other.items())
        elif hasattr(other, "keys"):
            _single_iterator(self, other, other.keys())
        else:
            _pairwise_iterator(self, other)

        _pairwise_iterator(self, kwds.items())

    def _keychecker(self, item):
        '''Normalize enumerated values for `linkname` and `linktype`'''

        if isinstance(item, (list, tuple)) and len(item) == 2:
            linkname, linktype = item
            if isinstance(linkname, six.string_types):
                linkname = LINKNAMES[linkname]
            if isinstance(linktype, six.string_types):
                linktype = LINKTYPES[linktype]

            return linkname, linktype

        else:
            raise AssertionError(self.report_error)

    def _reportchecker(self, item):
        '''Normalize Report instances'''

        if isinstance(item, Report):
            return item

        elif isinstance(item, (list, tuple)) and len(item) == 2:
            return Report(*item)

        else:
            raise AssertionError(self.report_error)


# PRIVATE
# -------


def _pairwise_iterator(self, iterable):
    '''
    Exhaust iterator containing pair-wise elements, that is,
    key-value pairs, and sequentially add items to self.

    Args:
        iterable (iterable):    iterable with 2 items per element
    '''

    for linkname, value in iterable:
        for linktype, report in value.items():
            self[linkname, linktype] = report


def _single_iterator(self, other, iterable):
    '''
    Exhaust iterator containing single elements corresponding
    to object keys, and sequentially add key and other[element]
    to self.

    Args:
        iterable (iterable):    iterable with a single item per element
    '''

    for linkname in iterable:
        for linktype, report in other[linkname].items():
            self[linkname, linktype] = report


# DATA
# ----


REPORTS = ReportStorage(REPORT_PATH,
    reports={
        LINKNAMES['Standard']: {
            LINKTYPES['interlink']: Report('Interlinks', sheets={
                'report': True,
                'best_peptide': True,
                'best_peptide_file': True,
                'comparative': True,
                'comparative_commonname': True,
                'quantitative': True,
                'quantitative_comparative': True,
                'skyline': True,
                'overall': True
            }),
            LINKTYPES['intralink']: Report('Intralinks', sheets={
                'report': True,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            }),
            LINKTYPES['deadend']: Report('DeadEnds', sheets={
                'report': True,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            })
        },
        LINKNAMES['Low Confidence']: {
            LINKTYPES['interlink']: Report('Low Confidence Interlinks', sheets={
                'report': True,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            }),
            LINKTYPES['intralink']: Report('Low Confidence Intralinks', sheets={
                'report': False,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            }),
            LINKTYPES['deadend']: Report('Low Confidence DeadEnds', sheets={
                'report': False,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            })
        },
        LINKNAMES['Fingerprint']: {
            LINKTYPES['interlink']: Report('Mass Fingerprint Interlinks', sheets={
                'report': True,
                'best_peptide': False,
                'best_peptide_file': False,
                'comparative': False,
                'comparative_commonname': False,
                'quantitative': False,
                'quantitative_comparative': False,
                'skyline': False,
                'overall': True
            })
        },
        LINKNAMES['Incomplete']: {
            # incomplete sheets do not mass back to the precursor, so they
            # only can be in the end report and with their own sheet
            LINKTYPES['multilink']: Report('Multilinks', sheets={
                'report': True,
                'overall': True
            }),
            LINKTYPES['single']: Report('Singles', sheets={
                'report': True,
                'overall': True
            })
        }},
    order=[
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='quantitative'),
        Independent(
            linkname=LINKNAMES['Fingerprint'],
            linktype=LINKTYPES['interlink'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='best_peptide_file'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='comparative'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='quantitative_comparative'),
        Dependent(sheet='skyline'),
        Dependent(sheet='overall'),
        Independent(
            linkname=LINKNAMES['Low Confidence'],
            linktype=LINKTYPES['interlink'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Incomplete'],
            linktype=LINKTYPES['multilink'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Incomplete'],
            linktype=LINKTYPES['single'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='best_peptide'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['interlink'],
            sheet='comparative_named'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['deadend'],
            sheet='report'),
        Independent(
            linkname=LINKNAMES['Standard'],
            linktype=LINKTYPES['intralink'],
            sheet='report'),
    ]
)
