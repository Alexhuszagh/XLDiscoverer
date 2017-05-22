'''
    Objects/Documents/sorting
    _________________________

    Tools to sort models and therefore alter the model order.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib.controllers import messages
from xldlib import exception
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, math_

# KEYS
# ----

SORT_KEYS = {
    'Peptide': "sortpeptide",
    'RT': "sortrt",
    'Score': "sortscore",
    'EV': "sortev",
    "Mod Count": "sortmodificationcounts"
}


# SORTING
# -------


@logger.init('document', 'DEBUG')
class DocumentSorter(messages.BaseMessage):
    '''
    Provides various sort keys to sort a document from by peptide,
    retention time, score, expectation value, or modification count.
    '''

    def __init__(self, mode, parent):
        super(DocumentSorter, self).__init__(parent)

        self.mode = mode

    @logger.call('document', 'debug')
    @messages.warningbox(KeyError)
    def __call__(self, **kwds):
        '''Sorts the spectral document on call'''

        if self.document is not None:
            key = self.getkey(kwds)
            indexes = self.getindexes(kwds)
            reverse = self.getreverse(key, kwds)
            try:
                fun = getattr(self, SORT_KEYS[key])
                fun(indexes, reverse=reverse)
            except KeyError:
                raise KeyError(exception.CODES['021'])

    #    PROPERTIES

    @property
    def document(self):
        return self.parent().document

    #      GETTERS

    def getkey(self, kwds):
        sortkey = '{}_sortkey'.format(self.mode)
        return kwds.get('key', defaults.DEFAULTS[sortkey])

    def getindexes(self, kwds):
        return kwds.get('indexes', range(len(self.document)))

    def getreverse(self, key, kwds):
        sort_reverse = '{}_sort_reverse'.format(self.mode)
        default = defaults.DEFAULTS[sort_reverse]
        if key == 'EV':
            # want to sort expectation values in descending order
            default = not default
        return kwds.get('reverse', default)

    #     SORTING

    def sortpeptide(self, indexes, reverse):
        '''Sorts the given transitions by peptide alphabetically'''

        self.__sort(self.__peptidekey, indexes, reverse)

    def sortrt(self, indexes, reverse):
        '''Sorts the give transitions based on retention time'''

        self.__sort(self.__rtkey, indexes, reverse)

    def sortscore(self, indexes, reverse):
        '''Sorts the given transitions based on the score'''

        self.__sort(self.__scorekey, indexes, reverse)

    def sortev(self, indexes, reverse):
        '''Sorts the given transitions based on expectation value'''

        self.__sort(self.__evkey, indexes, reverse)

    def sortmodificationcounts(self, indexes, reverse):
        '''Sorts the given transitions based on the the min mod counts'''

        self.__sort(self.__modificationcountkey, indexes, reverse)

    def __sort(self, sortkey, indexes, reverse):
        '''Arbitrary sort implementation with a given key'''

        for index in indexes:
            transitionfile = self.document[index]
            transitionfile.children.sort(key=sortkey, reverse=reverse)
            self.__relevel(transitionfile)

    def __relevel(self, transitionfile):
        '''Reindexes the given items post sorting to keep uniform levels'''

        for index, item in enumerate(transitionfile.children):
            item['attrs']['level'] = str(index)

    #      KEYS

    def __peptidekey(self, item):
        '''Sorts based on the alpha characters in the peptide sequence'''

        return '-'.join(item['attrs']['peptide'])

    def __rtkey(self, item):
        '''Sorts based on the floating point retention times'''

        if self.mode == 'transition':
            return np.min(item['attrs']['precursor_rt'])
        elif self.mode == 'fingerprint':
            return item['attrs']['precursor_rt']

    def __scorekey(self, item):
        '''Sorts based on the floating point peptide scores'''

        return np.mean(math_.to_num(item['attrs']['score']))

    def __evkey(self, item):
        '''Sorts based on the floating point expectation values'''

        return np.mean(math_.to_num(item['attrs']['ev']))

    def __modificationcountkey(self, item):
        '''Sorts based on the number of modifications in a peptide'''

        if self.mode == 'transition':
            modifications = item['crosslink'][0]['attrs']['modifications']
            modifications = [i.unpack() for i in modifications]

        return sum(len(i) for item in modifications for i in item.values())
