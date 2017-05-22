'''
    Definitions/modules
    ___________________

    Simplifies imports between Python2 and 3 by specifying module
    imports for specific types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

try:
    # re2 has superior performance generally speaking to re, however,
    # this is somewhat limited in a few cases

    # Performance tests:
    # time python -c "import re2; re2.match(\"^(a?){25}(a){25}$\", 'a'*25)"
    # 0m0.010s

    # time python -c "import re; re.match(\"^(a?){25}(a){25}$\", 'a'*25)"
    # 0m10.206s

    # Or, re2 is 1000x faster due to the exponential growth in Python SREs
    # The DFAs in re2 have a linear or polynomial expansion, making them
    # much faster.

    import re2 as re
    # set this for proper pattern checking, to test if compiled
    re._pattern_type = re.Pattern
except (NameError, ImportError):
    # basestring isn't properly defined on re2
    import re

# load objects/functions
if six.PY2:
    import cPickle as pickle
    import httplib

else:
    import pickle
    import http.client as httplib

__all__ = [
    're',
    'pickle',
    'httplib'
]
