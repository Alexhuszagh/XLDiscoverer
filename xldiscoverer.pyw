#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    xldiscoverer
    ____________

    GUI launcher for XL Discoverer. Core modules can be imported
    without the GUI loop by importing the xldlib package.

    $ python xldiscoverer.py --help
    usage: xldiscoverer.py [-h] [-l {INFO,WARN,DEBUG}] [-f {INFO,WARN,DEBUG}]
        [-o] [-e]

    optional arguments:
      -h, --help            show this help message and exit
      -l {INFO,WARN,DEBUG}, --log {INFO,WARN,DEBUG}
                            Log level
      -f {INFO,WARN,DEBUG}, --ftp-threshold {INFO,WARN,DEBUG}
                            Threshold for FTP Log level
      -o, --stdout          Remove stdout
      -e, --stderr          Remove stderr

    $ python
    >>> # initialize the QApplication before creating any objects
    ... from xldlib.onstart import main
    >>> from xldlib.resources import chemical_defs
    >>> chemical_defs.MODIFICATIONS[1]
    Modification(id=1, name='Acetohydrazide', formula='C2 H4 N2', aminoacid='', terminus=4, uncleaved=False, active=False, type=1, engine=1, neutralloss='', hidden=0)
'''

# load modules
import multiprocessing

# ONSTART
# -------

if __name__ == '__main__':
    # for multiprocessing, ensure we do not duplicate the full interpreter
    multiprocessing.freeze_support()

    from xldlib.onstart import launch
    launch.window()
