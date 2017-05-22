'''
    XlPy/Spectra/mzdata
    ___________________

    Not implemented parser for a depricated XML spectral file format
        -> Implement only if necessary

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

raise NotImplementedError

# load modules
import xml.sax

from xldlib.utils import logger

# ------------------
#      XML.SAX
# ------------------


@logger.init('scans', level='DEBUG')
class RunHandler(xml.sax.handler.ContentHandler):
    '''Grabs data from whole run.'''

    def __init__(self, data, engine):
        xml.sax.ContentHandler.__init__(self)

        self.data = data
        self.engine = engine
        self.subs = self.engine.get("subs", {})
        self.remove = self.engine.get("remove", [])
        self.process = {}

# ------------------
#       PARSER
# ------------------


@logger.init('scans', level='DEBUG')
class ParseMzData(object):
    '''Need to doc...'''

    def __init__(self, fileobj, grp, **kwargs):
        super(ParseMzData, self).__init__()

        self.fileobj = fileobj
        self.grp = grp

        #e = kwargs.get("format", "mzData")
        #v = kwargs.get("version", "3.65.0")
        #self.raw = scans.RAW[e][v]

