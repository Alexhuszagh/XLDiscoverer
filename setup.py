#!/usr/bin/env python

'''
    setup
    _____

    This is the main setup script for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/XLDiscoverer.txt for more details.
'''

# load modules/submodules
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from xldlib import resources

# DEPENDENCIES
# ------------

DEPENDENCIES = [
    'numexp>=2.4',
    'numpy>=1.7.1',
    'PySide',
    'requests>1.5.1',
    'pyqtgraph',
    'scipy',
    'six',
    'namedlist',
    'XlsxWriter'
]


# SETTINGS
# --------

SHORT_DESCRIPTION = 'Cross-Linking Mass Spectrometry GUI & Toolkit'

LONG_DESCRIPTION = '''Cross-Link Discoverer, or XL Discoverer aims
to provide a complete toolkit accessible from a GUI for cross-linking
mass spectrometry identification, validation, and quantitation.

XL Discoverer also supports various file formats, including open source
formats, such as mzML, mzXML, MGF, as well as proprietary file formats
such as Thermo Raw Files.
'''

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering \:: Chemistry',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: Unix',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
]


# SETUP
# -----

setup(name='XL Discoverer',
      version=resources.VERSION,
      description=SHORT_DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=resources.AUTHOR,
      author_email=resources.AUTHOR_EMAIL,
      maintainer=resources.MAINTAINER,
      maintainer_email=resources.MAINTAINER_EMAIL,
      packages=['namedlist', 'pyqtgraph', 'six', 'test', 'xldlib'],
      package_data={'': [
          'licenses/*',
          'resources/png/*',
          'templates/*',
          'README.md',
      ]},
      include_package_data=True,
      install_requires=DEPENDENCIES,
      setup_requires=DEPENDENCIES,
      zip_safe=False,
     )
