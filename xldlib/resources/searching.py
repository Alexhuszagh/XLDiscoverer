'''
    Resources/Parameters/searching
    ______________________________

    Function definitions for search/replace queries.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.definitions import re
from .parameters import defaults


# FUNCTIONS
# ---------

#
#
#def getreplace():
#    '''Returns the search regex and the replace string for string subs'''
#
#    replace = defaults.DEFAULTS['replace_form']
#    casesensitive = defaults.DEFAULTS['search_case_sensitive']
#    if not casesensitive:
#        search = re.compile(defaults.DEFAULTS['search_form'], re.I)
#    else:
#        search = re.compile(defaults.DEFAULTS['search_form'])
#
#    return search, replace


def get_search():
    '''Returns the search query for string matching'''

    if not defaults.DEFAULTS['search_case_sensitive']:
        return re.compile(defaults.DEFAULTS['search_form'], re.I)
    else:
        return re.compile(defaults.DEFAULTS['search_form'])


def get_replace():
    search = get_search()
    replace = defaults.DEFAULTS['replace_form']
    return search, replace
