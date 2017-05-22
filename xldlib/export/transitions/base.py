'''
    Export/Transitions/base
    _______________________

    Inheritable method definitions for transitions exporters.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import defaultdict, namedtuple

from xldlib.export import dataframes
from xldlib.objects import protein
from xldlib.qt.objects import base
from xldlib.resources.parameters import reports
from xldlib.utils import xictools


# OBJECTS
# -------

Crosslink = namedtuple("Crosslink", "linkname linktype")


class Memoizer(namedtuple("Memoizer", "seen frozen")):
    '''Subclass for default, mutable arguments'''

    def __new__(cls, seen=None, frozen=None):
        if seen is None:
            seen = {}
        if frozen is None:
            frozen = set()
        return super(Memoizer, cls).__new__(cls, seen, frozen)


# HELPERS
# -------


def getseen(labels):
    '''Returns a Seen instance from the spreadsheet data'''

    profile = labels.get_document().profile
    seen = dataframes.Seen.fromspreadsheet(labels.spreadsheet)

    for population, counts in labels.sequenced_population.items():
        crosslinker = profile.getheader(population)
        yield seen._replace(crosslinker=crosslinker), counts


def getintegrated(spreadsheet, headers, counts):
    '''Returns the integrated dataset from the header list'''

    integrated = []
    for header in headers:
        count = counts.get(header)
        val = xictools.IntegralData.fromspreadsheet(spreadsheet, header, count)
        integrated.append(val)

    return tuple(integrated)


# DATAFRAMES
# -----------


class Dataframe(dataframes.QuantitativeDataframe):
    '''Export dataframe for the integrated parameters'''

    #      GETTERS

    def getamplitudes(self, labelslist):
        '''Maps each linkage string to a a set of integrated data'''

        amplitudes = dataframes.Amplitudes(self.ratios)

        for labels in labelslist:
            spreadsheet = labels.spreadsheet
            headers = self.getheaders(labels)
            counts = labels.getusedheaders()
            integrated = getintegrated(spreadsheet, headers, counts)

            # get the key
            linkage = spreadsheet.getlinkage()
            filename = spreadsheet.getsearch()
            file_obj = amplitudes.checknew(filename)
            file_obj[linkage].add(integrated)

        return amplitudes.filter()

    def getheaders(self, labels):
        # TODO: make property
        return [self.profile.getheader(i.populations) for i in labels]


class HierarchicalDataframe(dataframes.HierarchicalDataframe):
    '''Export dataframe with hierarchical header definitions'''


# WORKSHEETS
# ----------


class ProteinsDummy(namedtuple("ProteinsDummy", "mapping")):
    '''Dummy proteins object to match the SQLite one'''

    def __new__(cls, mapping=None, **kwds):
        '''Initializes a mapping data structure for fake data lookups'''

        if mapping is None:
            mapping = {i: {} for i in protein.PROTEIN_FIELDS}
        mapping.update(kwds)

        return super(ProteinsDummy, cls).__new__(cls, mapping)


class WorksheetExport(base.BaseObject):
    '''Inheritable methods for dataframe export'''

    proteins = ProteinsDummy()

    #     GETTERS

    def getcrosslinks(self, document):
        '''Returns a unique list of Crosslink instances in the document'''

        crosslinks = defaultdict(list)
        with document.togglememory():
            for transition_file in document:
                for labels in transition_file:

                    attrs = (getattr(labels, i) for i in Crosslink._fields)
                    item = Crosslink(*attrs)
                    crosslinks[item].append(labels)

        return crosslinks

    def getsheets(self, crosslinks, sheet='quantitative'):
        '''Sets the sheets included for the report'''

        independent = [reports.Independent(sheet=sheet, *(i))
                       for i in sorted(crosslinks)]
        return [reports.Sheet.fromorder(i) for i in independent]

    def getlinkages(self, labels_list):
        '''Generates the linkage from a labels list'''

        linkages = []
        memoizer = Memoizer()

        for index, labels in enumerate(labels_list):
            for seen, count in getseen(labels):
                linkage = self.__getlinkage(seen, memoizer, labels, count)
                linkages.append(linkage)

        return [dataframes.Linkage.fromdict(i) for i in linkages]

    def __getlinkage(self, seen, memoizer, *args):
        '''Branched logic to internally return or increment a new linkage'''

        if seen in memoizer.seen:
            return self.increment(seen, memoizer, *args)
        else:
            return self.newlinkage(seen, memoizer, *args)

    #     HELPERS

    def increment(self, seen, memoizer, labels, count):
        '''Increments the counts on a singular linkage item'''

        linkage = memoizer.seen[seen]
        linkage['count'] += count

        if labels.frozen not in memoizer.frozen and bool(count):
            memoizer.frozen.add(labels.frozen)
            linkage['unique'] += 1

        return linkage

    def newlinkage(self, seen, memoizer, labels, count):
        '''Instantiate a new linkage instance'''

        linkage = seen.tolinkage(self.proteins, labels.frozen, count=count)
        memoizer.seen[seen] = linkage
        memoizer.frozen.add(labels.frozen)

        return linkage
