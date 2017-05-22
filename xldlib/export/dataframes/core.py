'''
    Export/Dataframes/core
    ______________________

    Core dataframe producer, which creates independent dataframes
    on the fly and builds

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import weakref

from xldlib.qt.objects import base
from xldlib.resources.parameters import reports
from xldlib.utils import logger

from . import best_peptide, comparative, overall, quantitative, report, skyline

# load objects/functions
from collections import namedtuple

from xldlib.definitions import partial

# DATAFRAMES
# ----------

DATAFRAMES = {
    'best_peptide': best_peptide.Dataframe,
    'best_peptide_file': partial(best_peptide.Dataframe, infile=True),
    'comparative': comparative.Dataframe,
    'comparative_named': partial(comparative.Dataframe,
        flags=comparative.FLAGS['named']),
    'quantitative_comparative': partial(comparative.Dataframe,
        flags=comparative.FLAGS['quantitative']),
    'overall': overall.Dataframe,
    'quantitative': quantitative.Dataframe,
    'report': report.Dataframe,
    'skyline': skyline.Dataframe,
}



# HELPERS
# -------


def get_linkage(seen, greylist, named, intrasubunit, frozen, count=1):
    '''Returns a dictionary with the linkage info'''

    return dict(
        string=seen.linkage,
        ids=seen.ids,
        subunits=seen.subunits,
        count=count,
        # {0, 1}
        unique=int(bool(count)),
        greylist=greylist,
        named=named,
        intrasubunit=intrasubunit,
        file=seen.file,
        crosslinker=seen.crosslinker,
        frozen=frozen)


def get_frozensingle(self, spreadsheet):
    '''Returns a frozen representation of a single link'''


# OBJECTS
# -------

Crosslink = namedtuple("Crosslink", "row index crosslink")
Quantitative = namedtuple("Quantitative", "row index crosslink")


class Linkage(namedtuple("Linkage", "string ids subunits count unique "
    "greylist named intrasubunit file crosslinker frozen")):
    '''Linkage object specific to files and crosslinkers'''

    #  CLASS METHODS

    @classmethod
    def fromdict(cls, obj):
        return cls(**obj)

    #    GETTERS

    def getsubunit(self):
        '''
        >>> self.subunits, self.getsubunit()
        (('1', '1'), '1')
        >>> self.subunits, self.getsubunit()
        (('1', '2'), '1-2')
        '''

        if all(i == self.subunits[0] for i in self.subunits[1:]):
            return self.subunits[0]
        else:
            return u'-'.join(self.subunits)

    #    HELPERS

    def toseen(self):
        return Seen(self.file, self.crosslinker, self.string,
                    self.ids, self.subunits)


class Seen(namedtuple("Seen", "file crosslinker linkage ids subunits")):
    '''Memoizer to avoid redundant data processing'''

    #  CLASS METHODS

    @classmethod
    def fromspreadsheet(cls, spreadsheet):
        '''Initializes a seen instance from various heterogeneous data'''

        return cls(
            spreadsheet.getsearch(),
            spreadsheet.getcrosslinker(),
            spreadsheet.getlinkage(),
            spreadsheet.getids(),
            spreadsheet.getnames()
        )

    #     PUBLIC

    def isgreylist(self, proteins):
        return any(i in proteins.mapping['greylist'] for i in self.ids)

    def isnamed(self, proteins):
        return any(i in proteins.mapping['named'] for i in self.ids)

    def isintrasubunit(self):
        return all(i == self.ids[0] for i in self.ids)

    def tolinkage(self, proteins, frozen, **kwds):
        '''Creates a new linkage'''

        greylist = self.isgreylist(proteins)
        named = self.isnamed(proteins)
        intrasubunit = self.isintrasubunit()

        return get_linkage(self, greylist, named, intrasubunit, frozen, **kwds)


@logger.init('spreadsheet', level='DEBUG')
class Memoizer(object):
    '''Memoizer for seen instances, using coupled sets and dicts'''

    def __init__(self, matched, proteins, key):
        super(Memoizer, self).__init__()

        self.matched = matched
        self.proteins = proteins
        self.key = key

        self.memo = {}
        self.frozen = set()
        self.linkages = {}

    def __call__(self, crosslink):
        '''pass'''

        data = self.matched[crosslink.row]
        spreadsheet = data['spreadsheet'][self.key][crosslink.index]
        seen = Seen.fromspreadsheet(spreadsheet)
        if seen in self.memo:
            self.incrementlinkage(crosslink, seen)
        else:
            self.newlinkage(crosslink, seen)

    #    PUBLIC

    def incrementlinkage(self, crosslink, seen):
        '''Increment the counters in the linkage'''

        linkage = self.memo[seen]
        linkage['count'] += 1
        if crosslink.crosslink.frozen not in self.frozen:
            self.frozen.add(crosslink.crosslink.frozen)
            linkage['unique'] += 1
        self.linkages[(crosslink.row, crosslink.index)] = linkage

    def newlinkage(self, crosslink, seen):
        '''Add a new linkage to self.linkages'''

        linkage = seen.tolinkage(self.proteins, crosslink.crosslink.frozen)
        self.memo[seen] = linkage
        self.frozen.add(crosslink.crosslink.frozen)
        self.linkages[(crosslink.row, crosslink.index)] = linkage


# HELPERS
# -------


def getspreadsheekey(sheet):
    '''Returns the spreadsheet key, dependent on the sheet type'''

    if sheet.linktype == reports.LINKTYPES['single']:
        return 'singles'
    elif sheet.name == 'quantitative':
        return 'labeled'
    else:
        return 'crosslinks'


# DATAFRAMES
# ----------


@logger.init('spreadsheet', level='DEBUG')
class DataframeCreator(base.BaseObject):
    '''
    Core dataframe creator. Initializes the dependent dataframes
    and instantiates all others on the fly.
    '''

    def __init__(self, matched, proteins, sheets):
        super(DataframeCreator, self).__init__()

        self.matched = matched
        self.proteins = proteins

        self.setsource()
        self.setdependentdataframes(sheets)

    @logger.call('report', level='DEBUG')
    def __call__(self, sheet):
        '''Returns the dataframe from a given report sheet'''

        # create the initial dataframes
        cls = DATAFRAMES[sheet.name]
        dataframe = cls(self.matched, sheet)
        crosslinks = list(self.getcrosslinks(sheet))
        self.setcounts(sheet, crosslinks)

        key = getspreadsheekey(sheet)
        linkages = self.getlinkages(crosslinks, key)

        if crosslinks:
            dataframe(crosslinks, linkages)
            self.processdependent(sheet, crosslinks, linkages)
        else:
            dataframe.set_default_columns()

        return dataframe

    def processdependent(self, sheet, crosslinks, linkages):
        '''Processes the dependent dataframes from the crosslink data'''

        # only uses the report dataframe to add to the dependent dataframes
        if sheet.name == 'report':
            for name in reports.DEPENDENT_REPORTS._names:
                if sheet.reports.sheets.get(name):
                    self.dependents[name](crosslinks, linkages)

    #     SETTERS

    def setsource(self):
        '''Sets the source thread (defaults to None if no thread)'''

        try:
            self.source = weakref.proxy(self.app.discovererthread)
        except KeyError:
            self.source = None

    def setdependentdataframes(self, sheets):
        '''Sets the dependent dataframes'''

        self.dependents = {}
        for sheet in sheets:
            if sheet.type == reports.REPORT_TYPES['dependent']:
                dataframe = DATAFRAMES[sheet.name](self.matched, sheet)
                self.dependents[sheet.name] = dataframe

    def setcounts(self, sheet, crosslinks):
        '''Sets the crosslink counts if a source thread exists'''

        if sheet.name == 'report' and  self.source is not None:
            self.source.helper.counts.add(crosslinks)

    #     GETTERS

    def getcrosslinks(self, sheet):
        '''Returns all crosslinks with a (file, crosslink) pair'''

        if sheet.linktype == reports.LINKTYPES['single']:
            return self.__getsingles()
        elif sheet.name == 'quantitative':
            return self.__getquantitative(sheet)
        else:
            return self.__getcrosslinks(sheet)

    def __getsingles(self):
        '''Returns the singles, unmatched, potential crosslinks'''

        for row, data in enumerate(self.matched):
            for index, single in enumerate(data['singles']):
                yield Crosslink(row, index, single)

    def __getquantitative(self, sheet):
        return self.__getcrosslinks(sheet, 'labeledcrosslinks', Quantitative)

    def __getcrosslinks(self, sheet, key='crosslinks', cls=Crosslink):
        '''Returns the crosslinks identified (no singles)'''

        for row, data in enumerate(self.matched):
            for index, crosslink in enumerate(data[key]):
                if self.isfilteredcrosslink(sheet, data, crosslink, key):
                    yield cls(row, index, crosslink)

    def getlinkages(self, crosslinks, key):
        '''Returns the linkages for dataframe processing'''

        memoizer = Memoizer(self.matched, self.proteins, key)
        for index, crosslink in enumerate(crosslinks):
            memoizer(crosslink)
        return {k: Linkage.fromdict(v) for k, v in memoizer.linkages.items()}

    #     CHECKERS

    def isfilteredcrosslink(self, sheet, data, item, key='crosslinks'):
        '''Checks a crosslink to ensure proper linkname/type'''

        if key == 'crosslinks':
            return item.name == sheet.linkname and item.type == sheet.linktype
        elif key == 'labeledcrosslinks':
            crosslink = data['crosslinks'][item.index]

            return self.isfilteredcrosslink(sheet, data, crosslink)
