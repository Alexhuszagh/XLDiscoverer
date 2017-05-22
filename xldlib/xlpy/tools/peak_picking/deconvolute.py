'''
    XlPy/Tools/Peak_Picking/deconvolute
    ___________________________________

    Function to deconvolute peaks from profile data

    :copyright: 2005-2013 Martin Strohalm <www.mmass.org>
    :modified: Alex Huszagh
    :license: GNU GPL, see licenses/mMass.txt for more details.
'''

# load modules
import copy
from xldlib.utils import masstools


# FUNCTIONS
# ---------


def deconvolute(peaklist):
    """Recalculate peaklist to singly charged.
        peaklist (mspy.peaklist) - peak list to deconvolute
    """

    # recalculate peaks
    buff = []
    for peak in copy.deepcopy(peaklist):

        # uncharged peak
        if not peak.charge:
            continue

        # charge is correct
        elif abs(peak.charge) == 1:
            buff.append(peak)

        # recalculate peak
        else:

            # set fwhm
            if peak.fwhm:
                new_fwhm = abs(peak.fwhm * peak.charge)
                peak.setfwhm(new_fwhm)

            # set m/z and charge
            if peak.charge < 0:
                new_mz = masstools.mz(peak.mz, -1, peak.charge)
                peak.set_mz(new_mz)
                peak.setcharge(-1)

            else:
                new_mz = masstools.mz(peak.mz, 1, peak.charge)
                peak.set_mz(new_mz)
                peak.setcharge(1)

            # store peak
            buff.append(peak)

    # remove baseline
    if buff:
        for peak in buff:
            peak.setsn(None)
            peak.setai(peak.intensity)
            peak.setbase(0.)

    # update peaklist
    return type(peaklist)(buff)
