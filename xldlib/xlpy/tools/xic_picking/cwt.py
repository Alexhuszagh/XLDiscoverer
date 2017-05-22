'''
    XlPy/Tools/Xic_Picking/cwt
    __________________________

    Quick continuous wavelet (CWT) deconvolution of the extracted
    ion chromatograms to find candidate peaks, which are then
    scores using biophysical parameters.
        DOI: 10.1093/bioinformatics/btl355

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np
from scipy import signal

from . import objects, picking, weighting


# BOUNDING
# --------


def get_peaks(peaks, localmin, last_index):
    '''Provides the start and end bounds for each peak by finding local min'''

    for peak in peaks:
        start = np.r_[0, localmin[np.where(localmin < peak)]][-1]
        end = np.r_[localmin[np.where(localmin > peak)], last_index][0]
        yield objects.Bounds(start, end)


def get_clusters(xicfit, peaks):
    '''Returns the weight for the bounds'''

    for peak in peaks:
        arrange = np.arange(peak.start, peak.end)

        isotopes = [[i[arrange] for i in item] for item in xicfit.isotopes]
        yield picking.Cluster(xicfit, peak.start, peak.end)


def boundcwt(xicfit, min_width=2, max_width=6, wavelet=signal.ricker, **kwds):
    '''
    Uses a continuous wavelet to find peaks from the extracted ion
    chromatograms, which are then expanded by finding the nearest
    local minima below a certain max threshold.

    Correlation between isotopes and the retention time similarity to
    anchors (points where the peptide was sequenced) enable selection
    of the best identified peak and XIC bounding.

    Fairly wide peaks are preferable for the wavelet, since the range is
    limited, the data is noisy (so overfitting is easy), and results
    can be validated by biophysical properties later.
    '''

    width = np.arange(min_width, max_width)
    peaks = signal.find_peaks_cwt(xicfit.y, width, wavelet=wavelet)
    localmin = picking.get_localminima(xicfit.y)
    peaks = list(get_peaks(peaks, localmin, xicfit.y.size - 1))
    clusters = list(get_clusters(xicfit, peaks))

    # calculate the weighting
    isotopes = weighting.get_isotope_weight(clusters, **kwds)
    anchors = weighting.get_anchor_weight(clusters)
    weighted = isotopes * anchors

    if not weighted.size:
        return objects.WeightedXicBounds(0, xicfit.y.size - 1, 0.)
    else:
        # get the maximum value from our weighting
        index = np.unravel_index(np.argmax(weighted), weighted.shape)
        cluster = clusters[index[1]]

        return objects.WeightedXicBounds.fromcluster(cluster, weighted[index])
