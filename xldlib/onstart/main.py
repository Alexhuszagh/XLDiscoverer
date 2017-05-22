'''
    Onstart/main
    ____________

    Initializes XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# INITIATE APP
# ------------

__all__ = [
    'APP'
]

from . import app
APP = app.App([])
