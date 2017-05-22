'''
    Utils/Xictools/metrics
    ______________________

    Metrics for XIC ratio filtering and processing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.resources.parameters import defaults

# load objects/functions
from collections import namedtuple

# OBJECTS
# -------


class Metrics(namedtuple("Metrics", "score ev fit")):
    '''Definitions for identification metrics'''

    #  CLASS METHODS

    @classmethod
    def fromspreadsheet(cls, spreadsheet, header):
        return cls(spreadsheet.getscore(),
            spreadsheet.getev(),
            spreadsheet[(header, 'XIC Fit Score')])

    @classmethod
    def fromcrosslink(cls, crosslink):
        header = crosslink.get_header()
        spreadsheet = crosslink.get_labels().getattr('spreadsheet')
        return cls.fromspreadsheet(spreadsheet, header)

    #     PUBLIC

    def isabovethreshold(self):
        return all((
            self.checkscore(),
            self.checkev(),
            self.checkfit()
        ))

    def checkscore(self, key='transition_score_threshold'):
        return all(i > defaults.DEFAULTS[key] for i in self.score)

    def checkev(self, key='transition_ev_threshold'):
        return all(i < defaults.DEFAULTS[key] for i in self.ev)

    def checkfit(self, key='transition_peakscore_threshold'):
        return self.fit > defaults.DEFAULTS[key]
