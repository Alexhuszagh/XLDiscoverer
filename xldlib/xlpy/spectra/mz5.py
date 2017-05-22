'''
    XlPy/Spectra/mz5
    ________________

    Not yet fully implemented parser for the MS HDF5 format, .mz5

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

raise NotImplementedError

# load modules
from models import scans
from xldlib.utils import logger

# load objects/functions
try:
    import h5py
    # values 2.3 and below do not have TypeVlenID support
    # (Variable len strings)
    assert float(h5py.__version__[:3]) > 2.3
except (AssertionError, ImportError):
    # add to log
    import traceback
    trace = traceback.format_exc()
    logger.Logging.error(trace)
    raise ImportError("Suitable h5py installation not found")

# ------------------
#      PARSER
# ------------------


class ParseMz5(object):
    '''
    Parses mz5 file format (hierarchical data format 5) and
    stores in dictionary.
    mz5 Format:
        /ChomatogramTime    # len = 6118,
            [3.10000000e-03, 2.01483333e-02, 3.49550000e-02]
            # rententionTime
        /ChromatogramList
        /ChromatogramIndex
        /ChromatogramIntensity  # len = 6118,
            [..] # basePeakIntensity
        /DataProcessing
        /SpectrumIntensity  # len = 25433359,
            [..., 924.1092529296875, 744.54937744140625, ...]
        /SpectrumIndex      # len = 6118,
            [..., 4279, 25433359] # index of end of each scan
    '''

    def __init__(self, fileobj, grp, source, **kwargs):
        super(ParseMz5, self).__init__()

        logger.Logging.info("Initializing ParseMz5....")
        # set attributes
        # must open h5py.File by name, close fileobj first
        fileobj.close()
        self.fileobj = h5py.File(fileobj.name, "r")
        self.grp = grp
        self.source = source
        engine = kwargs.get("format", "mz5")
        version = kwargs.get("version", "1.0")
        self.raw = scans.RAW[engine][version]

    def run(self):
        '''On start'''

        # add to log
        logger.Logging.info("Parsing MZ5 file....")

        subs = self.raw.get("subs", {})
        tmp = {}
        # extract data, which are numpy arrays
        for key, lst in subs.items():
            data = self.fileobj[lst[0]].value.tolist()
            typ = lst[1]
            # set type cast
            if typ:
                data = [typ(i) for i in data]
            tmp[key] = data
        # process scans
        nums = tmp.get("num", [])
        for i, num in enumerate(nums):
            scan = {}
            self.data[num] = scan
            for k, lst in tmp.items():
                val = lst[i]
                scan[k] = val
