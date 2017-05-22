# -*- coding: utf-8 -*-
'''
    XlPy/Peptide_Database/sequencing
    ________________________________

    Contains data for generating theoretical mass tables for
    searching peptide sequencing ions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# contains remenants for sequencing ions by CID or ECD
#   http://biochem.ncsu.edu/MassSpec/docs/PeptideSequencingMS.pdf

# Collision Induced Dissociation
# Base off mascot
#   b, y, a
#       H2O and NH3 loss?
# If precursor 2+, look for 2+ ion series as well
#   ESI + Ion Trap
#       Looks only at y/b-ions
#   qqTOF
#   MALDI PSD
#       http://www.matrixscience.com/msparser/help/classmatrix__science_1_1ms__fragmentationrules.html#aa512e562f208dfbdbbfe781884c22df9
#       http://www.matrixscience.com/help/fragmentation_help.html

# ECD
#   c, z


# What are the different ion series?

#       a   [N]+[M]-CHO
#       a*  a-NH3
#       a°  a-H2O
#       b   [N]+[M]-H
#       b*  b-NH3
#       b°  b-H2O
#       c   [N]+[M]+NH2
# d   a – partial side chain
# v   y – complete side chain
# w   z – partial side chain
# x   [C]+[M]+CO-H
#       y   [C]+[M]+H
#       y*  y-NH3
#       y°  y-H2O
#       z   [C]+[M]-NH2

# INTERNAL FRAGMENTATION
# min_internal_mass 0.0
# max_internal_mass 700.0

# FRAG_INTERNAL_YB
# Internal series, caused by double backbone cleavage. Combination of b type and y type cleavage.
#
# FRAG_INTERNAL_YA
# Internal series, caused by double backbone cleavage. Combination of a type and y type cleavage.
#
