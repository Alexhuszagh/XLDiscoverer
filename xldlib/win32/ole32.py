'''
    Win32/ole32
    ___________

    Pure Python functions for with object embedding and linking
    on Microsoft.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import datetime


def oadate(d_date):
    '''Converts a c_double OLE Automation Date to Python datetime'''

    adjusted = (d_date.value - 25569) * 24 * 3600
    return datetime.datetime.fromtimestamp(adjusted)
