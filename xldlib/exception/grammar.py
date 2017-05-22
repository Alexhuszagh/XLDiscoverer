'''
    Exceptions/grammar
    __________________

    Grammatical agreement conversion for words in error reporting.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

import six


# OBJECTS
# -------

GrammaticalNumber = namedlist("GrammaticalNumber", "singular plural")


# DATA
# ----

GRAMMATICAL_NUMBERS = {
    '-s': GrammaticalNumber("", "s"),
    '-at': GrammaticalNumber("at", "ose"),
    '-y': GrammaticalNumber("y", "ies"),
}

SINGULAR = {k: v.singular for k, v in GRAMMATICAL_NUMBERS.items()}
PLURAL = {k: v.plural for k, v in GRAMMATICAL_NUMBERS.items()}


# CONVERSIONS
# -----------


def convert_number(word, pluralize=False):
    '''
    Convert grammatical number placeholders within each word,
    defaulting to the singular grammatical number.

    Args:
        word (str):       word with included singular/plural placeholders
        pluralize (bool): singular or plural form
    '''

    pluralize = _pluralizechecker(pluralize)

    if pluralize:
        return word % PLURAL
    else:
        return word % SINGULAR


# PRIVATE
# -------


def _pluralizechecker(pluralize):
    '''Normalize pluralize types'''

    if isinstance(pluralize, bool):
        # booleans are considered integers in Python
        return pluralize
    elif isinstance(pluralize, six.integer_types):
        # check the numerical count is not 1, for singular
        return pluralize != 1
    elif isinstance(pluralize, (list, tuple)):
        # check the numerical count of items is not 1, for singular
        return len(pluralize) != 1
    return bool(pluralize)
