'''
    XlPy/matched/remove
    ___________________

    Helper class to remove base IDs from parsed modification lists.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import namedtuple

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# NAMES
# -----


class Threshold(namedtuple("Threshold", "score ev")):
    '''Scoring and expectation value thresholds for sequenced peptides'''

    @classmethod
    def fromrow(cls, row):
        '''Initializes from a xlpy.files.FileRow instance'''

        name = row.data['attrs']['engines']['matched'][0]
        score = defaults.DEFAULTS[name + ' Score']
        ev = defaults.DEFAULTS[name + ' EV']
        return cls(score, ev)


# DECORATORS
# ----------


def deleterows(f):
    '''Removes all indexes accumulated in the self.deleterows after f()'''

    def decorator(self, *args, **kwds):
        f(self, *args, **kwds)
        for row in self.deleterows[::-1]:
            self.row.data.deleterow(row)
        del self.deleterows[:]

    decorator.__name__ = f.__name__
    return decorator


# REMOVER
# -------


@logger.init('matched', 'DEBUG')
class RemoveIds(base.BaseObject):
    '''
    Methods to remove decoy, null, and other non-crosslinked peptide
    data.
    '''

    def __init__(self, row):
        super(RemoveIds, self).__init__()

        self.row = row
        self.deleterows = []
        self.threshold = Threshold.fromrow(row)

        source = self.app.discovererthread
        self.proteins = source.proteins
        self.fragments = source.parameters.fragments

    def __call__(self):
        '''Remove all the undesirable data on call'''

        self.databasefiltering()
        self.decoys()
        self.blacklist()
        self.nomodifications()
        self.nocrosslinkers()
        self.belowscore()

    #      REMOVERS

    def databasefiltering(self):
        '''
        Removes entries from list if not specified in database
        IDs from the user. Works off a tristate variable,
        <limited>, which can be set to 'null' (off), 'mild'
        (filters out all IDs not in the specified database),
        or 'strict' (filters out all scans with IDs not in the
        specified database).
        '''

        limited = self.proteins.get_limited(as_string=True)
        if limited == 'None':
            return
        elif limited == 'Mild':
            self.filtermild()
        else:
            self.filterstrict()

    @deleterows
    def decoys(self):
        '''Remove decoys, false ids during search for scoring'''

        decoys = set(list(self.proteins.mapping['decoys']))
        decoys.update(self.row.engines['matched'].defaults.decoys)

        rows = self.row.data.findrows('id', decoys)
        self.deleterows.extend(rows)

    @deleterows
    def blacklist(self):
        '''
        Removes blacklisted proteins, ideally proteins which are artifacts
        of sample preparation and can have no biological reality
        (or homology to biologically relevant proteins)!!
        '''

        rows = self.row.data.findrows('id', self.proteins.mapping['blacklist'])
        self.deleterows.extend(rows)

    @deleterows
    def nomodifications(self):
        '''
        Removes peptides without posttranslational modifications, which
        also includes those lacking crosslinker fragments.
        '''

        for row, mod in enumerate(self.row.data['matched']['modifications']):
            if not mod:
                self.deleterows.append(row)

    @deleterows
    def nocrosslinkers(self):
        '''
        Removes peptides without posttranslational modifications, which
        also includes those lacking crosslinker fragments.
        '''

        for index, mod in enumerate(self.row.data['matched']['modifications']):
            if not mod.intersect(self.fragments):
                self.deleterows.append(index)

    @deleterows
    def belowscore(self):
        '''
        Removes peptides identified below the scoring thresholds that
        have been deemed satisfactory for each search engine.
        These values are configurable via the Settings/Engines view
        or from Resources/Parameters/DEFAULTS
        '''

        scores, = self.row.data.columnmax('id', ['score'])
        evs, = self.row.data.columnmin('id', ['ev'])

        # need to traverse list twice, since need to enumerate all items for
        # the initial protein scores
        generator = self.row.data.iterrows(['id', 'score', 'ev'])
        for row, (uniprotid, score, ev) in enumerate(generator):
            protein_score = scores[uniprotid]
            protein_ev = evs[uniprotid]

            conditions = all((
                protein_score > self.threshold.score.protein,
                protein_ev < self.threshold.ev.protein,
                score > self.threshold.score.peptide,
                ev < self.threshold.ev.peptide
            ))
            if not conditions:
                self.deleterows.append(row)

    #      HELPERS

    @deleterows
    def filtermild(self):
        '''
        Removes only matched peptides with UniProt IDs outside the
        limited database
        '''

        found = self.row.data.findrows('id', self.proteins.mapping['proteins'])
        allrows = set(range(len(self.row.data['matched']['id'])))
        rows = allrows.difference(found)
        self.deleterows.extend(rows)

    @deleterows
    def filterstrict(self):
        '''
        Removes all MS3 scans with any matched peptide with a UniProt ID
        not in the limited database.
        '''

        grouped = self.row.data.groupby(fields=['id'])
        for values in grouped.values():
            rows, ids = ZIP(*values)
            if any(i not in self.proteins.mapping['proteins'] for i in ids):
                self.deleterows += rows
        self.deleterows.sort()
