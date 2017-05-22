'''
    Export/Dataframes/counter
    _________________________

    Linkage counters for hierarchical dataframes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import defaultdict

import numpy as np

from xldlib.utils import logger


# HELEPRS
# -------


def lenif(iterable):
    '''Returns the length of the iterable removing falsey items'''

    return len([i for i in iterable if i])


# TEMPLATES
# ---------


def counts_template():
    return {
        'count': defaultdict(int),
        'interaction': defaultdict(set)
    }


# COUNTERS
# --------


@logger.init('spreadsheet', level='DEBUG')
class IndexMemo(dict):
    '''Subclass to provide facile index setting/memoization'''

    def __init__(self, dataframe, linkageindex=1):
        super(IndexMemo, self).__init__()

        self.dataframe = dataframe
        self.linkageindex = linkageindex

    #      MAGIC

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''Checks the linkage string previous set or creates a new index'''

        if key in self:
            return dict_getitem(self, key)
        else:
            index = self.dataframe.get_last_index()
            column = self.dataframe.get_column(self.linkageindex)
            self[key] = index
            self.dataframe.loc[index, column] = key
            return index


@logger.init('spreadsheet', level='DEBUG')
class LinkageCounts(defaultdict):
    '''Subclass to provide facile linkage counting'''

    def __init__(self, counter, factory=list):
        super(LinkageCounts, self).__init__(factory)

        self.counter = counter

    #     SETTERS

    def setlinkage(self, linkage):
        self[linkage.string].append(self.counter(linkage))

    #     GETTERS

    def get_counts(self, key):
        return len(self[key])

    def get_sum(self, key):
        return sum(self[key])


@logger.init('spreadsheet', level='DEBUG')
class FileCounts(defaultdict):
    '''Subclass to provide facile linkage counting'''

    def __init__(self, counter, headers=None, factory=counts_template):
        super(FileCounts, self).__init__(factory)

        self.counter = counter
        if headers is not None:
            self.headers = {j: i for i, j in enumerate(headers)}

    #     SETTERS

    def setlinkage(self, linkage, key=None, ratio_obj=None):
        '''
        Sets the linkage counts using a counter mechanism if counts
        are not provided, else, it uses a ratio_obj added to add the
        normalized values and the remaining items.
        '''

        if key is None:
            key = linkage.file

        if ratio_obj is None:
            self.__setlinkagesingle(linkage, key)
        else:
            self.__setlinkageratio(linkage, key, ratio_obj)

    def __setlinkagesingle(self, linkage, key):
        '''Sets the linkage entry for a single counts item (no counters)'''

        self[key]['count'][linkage.string] += self.counter(linkage)
        self[key]['interaction'][linkage.getsubunit()] = None

    def __setlinkageratio(self, linkage, key, ratio_obj):
        '''Sets an array of values for linkage counts from a ratio object'''

        zeros = np.zeros(ratio_obj.counts.size)
        array = self[key]['count'].setdefault(linkage.string, zeros)

        # push the normalized value to the end
        counts = ratio_obj.counts.tolist()
        counts.append(counts.pop(ratio_obj.index))
        array += np.array(counts)

        # add interaction values
        subunit = linkage.getsubunit()
        for header, index in self.headers.items():
            if counts[index]:
                self[key]['interaction'][header].add(subunit)

        if counts[-1]:
            self[key]['interaction']['normalize'].add(subunit)


    #     GETTERS

    def get_counts(self, key, header=None):
        '''Returns the count of linkages'''

        if header is None:
            return len(self[key]['count'])
        else:
            keycounts = self.counts_from_index(key, self.headers[header])
            normalization = self.counts_from_index(key, -1)
            return '{0}/{1}'.format(lenif(keycounts), lenif(normalization))

    def get_sum(self, key, header=None):
        '''Returns the total sum of counts within the file'''

        if header is None and hasattr(self, "headers"):
            return sum(i.sum() for i in self[key]['count'].values())
        elif header is None:
            return sum(self[key]['count'].values())
        else:
            keycounts = self.counts_from_index(key, self.headers[header])
            normalization = self.counts_from_index(key, -1)
            return '{0}/{1}'.format(sum(keycounts), sum(normalization))

    def get_interactions(self, key, header=None):
        '''Returns the total number of interactions'''

        if header is None:
            return len(self[key]['interaction'])
        else:
            length = len(self[key]['interaction'][header])
            normalize = len(self[key]['interaction']['normalize'])
            return '{0}/{1}'.format(length, normalize)

    def counts_from_index(self, key, index):
        return (int(i[index]) for i in self[key]['count'].values())

    #      TOTALS

    def get_totalcounts(self):
        total = set()
        for values in self.values():
            total.update(list(values['count']))
        return len(total)

    def get_totalsum(self):
        return sum(self.get_sum(i) for i in self)

    def get_totalinteractions(self):
        total = set()
        for values in self.values():
            total.update(values['interaction'])
        return len(total)
