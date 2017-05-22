'''
    Definitions/classes
    ___________________

    Helper classes and class methods to simplify code between Python2 and 3.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import json

import six

if six.PY2:
    from HTMLParser import HTMLParser
    try:
        from thread import get_ident
    except ImportError:
        from dummy_thread import get_ident

    from urllib import quote, urlencode, unquote
    from urllib2 import HTTPError, Request, URLError, urlopen

else:
    from html.parser import HTMLParser
    try:
        from _thread import get_ident
    except ImportError:
        from _dummy_thread import get_ident

    from urllib.error import HTTPError
    from urllib.parse import quote, urlencode, unquote
    from urllib.request import Request, URLError, urlopen


__all__ = [
    'HTMLParser',
    'get_ident',
    'quote',
    'urlencode',
    'unquote',
    'HTTPError',
    'Request',
    'URLError',
    'urlopen',
    'Json',
    'partial'
]

# MODULE-LIKE
# -----------


class Json(object):
    '''Methods for the json module to help facilitate loading/dumping'''

    @staticmethod
    def dump(document, fileobj, **kwargs):
        '''Processes a given file to JSON, and updates the encoding if PY2'''

        if six.PY2:
            kwargs.update(encoding='utf-8')

        json.dump(document, fileobj, **kwargs)

    @staticmethod
    def load(fileobj, **kwargs):
        '''Loads from a json file to dict, and updates the encoding if PY2'''

        if six.PY2:
            kwargs.update(encoding='utf-8')
        return json.load(fileobj, **kwargs)


# FUNCTOOLS
# ---------


class partial(object):
    '''
    Creates an extended partial object where the function and arguments
    are passed along with the module name and doc
    '''

    def __init__(self, func, *args, **kwds):
        super(partial, self).__init__()

        self.func = func
        self.args = args
        self.kwds = kwds

        for magic in ('__name__', '__module__', '__doc__'):
            try:
                setattr(self, magic, getattr(self.func, magic))
            except AttributeError:
                pass

    def __call__(self, *args, **kwds):
        newargs = self.args + args
        newkwds = self.kwds.copy()
        newkwds.update(kwds)
        return self.func(*newargs, **newkwds)
