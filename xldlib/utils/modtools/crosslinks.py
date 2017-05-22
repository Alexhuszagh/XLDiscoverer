'''
    XlPy/Tools/Modtools/crosslinks
    ______________________________

    Tools for finding cross-linker positions and calculating scores

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import math

from xldlib.qt.objects import base
from xldlib.resources.parameters import reports
from xldlib.utils import logger

# WEIGHTS
# -------

NON_MONOISOTOPIC = -0.25
MIN_ISOTOPE_SPACING = 0.1       # assuming z < 10

WEIGHTS = {
    'product_ppm': 1,
    'product_ppm_sigma': 5.,
    'precursor_ppm': 1,
    'precursor_ppm_sigma': 10.,
    'min_score': 8.57,
    'other_scores': 20,
}


LINKNAME_WEIGHTS = {
    reports.LINKNAMES['Standard']: 10000,
    reports.LINKNAMES['Low Confidence']: 5000
}

# SCORING
# -------


@logger.init('crosslinking', 'DEBUG')
class ScoreCrossLinks(base.BaseObject):
    '''
    Calculates a score on the overall ID quality, primarily weighted
    based on the MS3 scores and MS2/MS3 PPMs, and secondarily on the
    MS3 EVs. This is because the MS3 EVs are sample-to-sample dependent,
    varying with the database size, while the PPMs and scores should be
    database size-independent.
    '''

    def __init__(self, data):
        super(ScoreCrossLinks, self).__init__()

        self.data = data

    @classmethod
    def fromrow(cls, row):
        return cls(row.data)

    def __call__(self, crosslink, keys=('ppm', 'score', 'ev')):
        '''Stores all the weights in a link instance'''

        weights = []
        data = {k: self.data.getcolumn(crosslink.index, k) for k in keys}
        if crosslink.type != reports.LINKTYPES['multilink']:
            weights.extend(self.getprecursorppms(crosslink))

        weights.extend(self.getproductppms(data))
        weights.extend(self.getproductscores(data))
        weights.extend(self.getproductevs(data))

        return sum(weights)

    #    GETTERS

    def getprecursorppms(self, link):
        '''
        Scores precursor ppms based on their quality, with a given weight,
        standard variance, assuming a normal distribution. Includes a
        correcting factor in case the MS1 monoisotopic parent was not
        selected.
        '''

        # a * math.exp(b**2 / (2c**2))
        exp = -(link.ppm ** 2) / (2 * (WEIGHTS['precursor_ppm_sigma'] ** 2))
        yield WEIGHTS['precursor_ppm'] * math.exp(exp)

        # else, correct score for no monoisotopic selection
        if abs(min(link.ppm_set) - link.ppm) > MIN_ISOTOPE_SPACING:
            yield NON_MONOISOTOPIC

    def getproductppms(self, data):
        '''
        Scores product ppms based on their quality, with a given weight,
        standard variance, assuming a normal distribution.
        '''

        for ppm in data['ppm']:
            # a * math.exp(b**2 / (2c**2))
            exp = -(ppm ** 2) / (2 * (WEIGHTS['product_ppm_sigma'] ** 2))
            yield WEIGHTS['product_ppm'] * math.exp(exp)

    def getproductscores(self, data):
        '''
        Weights scores based on a linear function. Includes two scores:
        one for the worst ID, which should be the most representative
        of the peptide ID quality, and is weighted the highest.
        '''

        scores = list(data['score'])
        lowestscore = min(scores)
        scores.remove(lowestscore)

        # grab weight for lowest score
        yield lowestscore / WEIGHTS['min_score']
        for score in scores:
            yield score / WEIGHTS['other_scores']

    def getproductevs(self, data):
        '''
        Weights expectation values. Assumes EVs follow a logarithmic
        distribution, and are weight the least stringently of any of the
        params, due to its variance with sample size.
        '''

        for ev in data['ev']:
            if ev <= 1:
                try:
                    yield math.sqrt(-math.log10(ev))
                except ValueError:
                    # bug in the Protein Prospector output
                    yield 0


# SORTING
# -------


@logger.init('crosslinking', 'DEBUG')
class SortLinks(base.BaseObject):
    '''
    Link sorter based on the link name and then scoring parameters,
    favoring high quality links (standard > low confidence), and then
    the various scoring parameters.
    '''

    def __init__(self, row, reverse=True):
        super(SortLinks, self).__init__()

        self.row = row
        self.scorer = ScoreCrossLinks.fromrow(row)
        self.reverse = reverse

    def __call__(self, crosslinks):
        '''Sorts the given crosslinks'''

        crosslinks.sort(key=self.scorekey, reverse=self.reverse)

    def scorekey(self, crosslink):
        '''
        Scores a link given the link name and score. Adjusts for the
        fact that precise IDs are much more relevant than crosslink score
        using arbitrary parameters.
        '''

        basescore = LINKNAME_WEIGHTS.get(crosslink.name, 0)
        return basescore + self.scorer(crosslink)
