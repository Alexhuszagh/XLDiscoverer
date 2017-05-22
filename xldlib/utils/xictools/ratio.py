'''
    Utils/Xictools/ratio
    ____________________

    Object definitions for spectral ratio calculation.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np

from xldlib import exception
from xldlib.resources.parameters import defaults

# load objects/functions
from collections import namedtuple

from xldlib.definitions import partial


# CONSTANTS
# ---------
INFINITY = u'\u221E'


# HELPERS
# -------


def get_normalization_index(ratios,
    normalize_mode=defaults.DEFAULTS['xic_normalization']):
    '''Returns the position within integrated to normalize'''

    if normalize_mode == 'Light':
        return 0
    elif normalize_mode == 'Medium' and ratios.shape[-1] <= 2:
        # label-free or Light/Heavy, return Heavy if possible
        return ratios.shape[-1] - 1
    elif normalize_mode == 'Medium':
        # 1+ Medium states, return heaviest "Medium index"
        return ratios.shape[-1] - 2
    elif normalize_mode == 'Heavy':
        return ratios.shape[-1] - 1
    elif normalize_mode == 'Min':
        return np.argmin(ratios)
    elif normalize_mode == 'Max':
        return np.argmax(ratios)


# OBJECTS
# -------


class Ratio(namedtuple("Ratio", "ratio index error counts")):
    '''Definitions for spectral ratios'''

    def __new__(cls, ratio, index, error=None, counts=None):
        return super(Ratio, cls).__new__(cls, ratio, index, error, counts)

    def tostr(self):
        '''Returns a string representation of the Ratio (and error)'''

        if self.error is not None:
            return self.getstring(self.ratio), self.getstring(self.error)
        else:
            return self.getstring(self.ratio)

    @staticmethod
    def getstring(array):
        '''Returns a string representation of the array'''

        if array is None:
            return '-'
        elif not isinstance(array, (np.ndarray, list, tuple)):
            return array
        else:
            return ':'.join(array)

    def getcounts(self, index):
        return '{0}/{1}'.format(self.counts[index], self.counts[self.index])


class Ratios(namedtuple("Ratios", "ratios noise index counts")):
    '''Ratios object which stores a variable-sized'''

    # ROUNDING
    # --------
    _round = partial(round, ndigits=3)
    _gtlt = partial(round, ndigits=1)

    def __new__(cls, ratios, noise, index=None, counts=None):

        # create our ratios
        ratios = cls.newarray(ratios)
        noise = cls.newarray(noise)

        if index is None:
            index = get_normalization_index(ratios)
        if counts is None:
            counts = [0] * ratios.shape[-1]

        return super(Ratios, cls).__new__(cls, ratios, noise, index, counts)

    #    CLASS METHODS

    @classmethod
    def fromintegrated(cls, attr, *items):
        '''Initializes the ratios object from integrated spectral data'''

        counts = np.sum([[i.counts or 0 for i in j] for j in items], axis=0)

        amplitudes = [[getattr(i, attr) for i in item] for item in items]
        ratios = [[i.value for i in item] for item in amplitudes]
        noise = [[i.baseline for i in item] for item in amplitudes]
        return cls(ratios, noise, counts=counts)

    @staticmethod
    def newarray(array):
        '''Standardized format for a Ratios-bound array'''

        array = np.array(array)
        if len(array.shape) == 1:
            array = array.reshape((1, -1))
        return array

    #     PUBLIC

    def normalize(self, error=False):
        '''Returns the normalized spectral ratio from the given index'''

        item = self._filternan()

        if not item.ratios.size:
            return Ratio('-', self.index, '-', counts=self.counts)
        elif defaults.DEFAULTS['weighted_comparative_ratio']:
            return item.getweightedratio(error)
        else:
            return item.getunweightedratio(error)

    def tostr(self, error=False):
        '''Returns a string representation of the ratio'''

        if error:
            return self.__alltostr()
        else:
            return self.__ratiotostr()

    #    NON-PUBLIC

    def _filternan(self):
        '''Remove NaN elements to avoid misleading ratio calculation'''

        naned = np.isnan(self.ratios)
        column_wise = ~(np.any(naned.T, axis=1) & ~np.all(naned.T, axis=1))
        boolean = np.all((~naned) | column_wise, axis=1)

        ratios = self.ratios[boolean]
        noise = self.noise[boolean]

#        items = (naned[i] for i in range(naned.shape[0]))
#        indexes = {i for i, j in enumerate(items) if j.any() and not j.all()}
#
#        ratios = [j for i, j in enumerate(self.ratios) if i not in indexes]
#        noise = [j for i, j in enumerate(self.noise) if i not in indexes]
        return self._replace(ratios=ratios, noise=noise)

    #    RATIOS

    @exception.silence_warning(RuntimeWarning)
    def getweightedratio(self, error=False):
        '''Returns the weighted ratios, summing by axis first'''

        estimated = False
        means = np.mean(np.nan_to_num(self.ratios), axis=0)

        if not means[self.index] and self.noise.T[self.index].any():
            normalized = self.__get_weighted_with_estimated_baseline(means)
            estimated = True
        elif not means[self.index]:
            normalized = INFINITY
            estimated = True
        else:
            normalized = self.__get_weighted_with_normal_baseline(means)

        if error and (not estimated) and self.ratios.shape[0] > 1:
            error = self.__get_weighted_error(means)
            return Ratio(normalized, self.index, error, counts=self.counts)
        elif error:
            return Ratio(normalized, self.index, '-', counts=self.counts)
        else:
            return Ratio(normalized, self.index, counts=self.counts)

    def __get_weighted_with_estimated_baseline(self, means):
        '''Returns the weighted ratio with an estimate baseline'''

        noisemean = np.mean(np.nan_to_num(self.noise), axis=0)
        baseline = noisemean[self.index]
        indexes = set(np.where(means == 0)[0])

        normalized = []
        for index in range(means.size):
            if index == self.index:
                normalized.append('1.0')
            elif index in indexes:
                normalized.append('-')
            else:
                rounded = str(self._gtlt(means[index]/baseline))
                normalized.append('>' + rounded)

        return normalized

    def __get_weighted_error(self, means):
        '''Returns the weighted standard deviation for the means'''

        ratios = self.ratios / self.ratios.T[self.index].reshape((-1, 1))
        weights = self.ratios.sum(axis=0)

        meanratio = means / means[self.index]
        variances = (ratios - meanratio)**2 * weights / weights.sum()
        return self.arrtostr(np.sqrt(variances.mean(axis=0)))

    def __get_weighted_with_normal_baseline(self, means):
        '''Returns the weighted ratio with a normal baseline'''

        noisemean = np.mean(np.nan_to_num(self.noise), axis=0)
        baseline = means[self.index]
        indexes = set(np.where(means == 0)[0])

        normalized = []
        for index in range(means.size):
            if index == self.index:
                normalized.append('1.0')
            elif index in indexes:
                rounded = str(self._gtlt(noisemean[index] / baseline))
                normalized.append('<' + rounded)
            else:
                rounded = str(self._round(means[index] / baseline))
                normalized.append(rounded)

        return normalized

    @exception.silence_warning(RuntimeWarning)
    def getunweightedratio(self, error=False):
        '''Returns the unweighted ratios, summing by axis first'''

        estimated = False
        if not self.noise.T[self.index].any():
            normalized = INFINITY
            estimated = True
        elif np.isnan(self.ratios.T[self.index]).all():
            normalized = self.__get_unweighted_with_estimated_baseline()
            estimated = True
        else:
            normalized = self.__get_unweighted_with_normal_baseline()

        if error and (not estimated) and self.ratios.shape[0] > 1:
            ratios = self.ratios / self.ratios.T[self.index].reshape((-1, 1))
            error = self.arrtostr(np.std(ratios, axis=0))
            return Ratio(normalized, self.index, error)
        elif error:
            return Ratio(normalized, self.index, '-')
        else:
            return Ratio(normalized, self.index)

    def __get_unweighted_with_estimated_baseline(self):
        '''Returns the unweighted ratio with an estimate baseline'''

        baseline = np.nan_to_num(self.noise).T[self.index]
        indexes = set(np.where(np.isnan(self.ratios).all(axis=0))[0])
        transposed = np.nan_to_num(self.ratios.T)

        normalized = []
        for index in range(self.ratios.shape[-1]):
            if index == self.index:
                normalized.append('1.0')
            elif index in indexes:
                normalized.append('-')
            else:
                rounded = str(self._gtlt(np.mean(transposed[index]/baseline)))
                normalized.append('>' + rounded)

        return normalized

    def __get_unweighted_with_normal_baseline(self):
        '''Returns the unweighted ratio with a normal baseline'''

        ratios = self.ratios.T
        noise = np.nan_to_num(self.noise).T
        baseline = ratios[self.index]
        indexes = set(np.where(np.isnan(self.ratios).all(axis=0))[0])

        normalized = []
        for index in range(self.ratios.shape[-1]):
            if index == self.index:
                normalized.append('1.0')

            elif index in indexes:
                rounded = str(self._gtlt(np.mean(noise[index]/baseline)))
                normalized.append('<' + rounded)
            else:
                rounded = str(self._round(np.mean(ratios[index]/baseline)))
                normalized.append(rounded)

        return normalized

    #  FORMATTING

    def __ratiotostr(self):
        '''Returns a string representation of the ratio without the error'''

        if np.isnan(self.ratios).all():
            return '-'
        else:
            return self.normalize().tostr()

    def __alltostr(self):
        '''Returns a string representation of the ratio without the error'''

        if np.isnan(self.ratios).all():
            return '-', '-'
        else:
            return self.normalize(error=True).tostr()

    #    HELPERS

    def arrtostr(self, array):
        return ['-' if np.isnan(i) else str(self._round(i)) for i in array]

