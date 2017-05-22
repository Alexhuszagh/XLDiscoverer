'''
    runtests
    ________

    Runs all of the unittests.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# load tests
import unittests


# SUITE
# -----


def run_suite():
    '''Run complete unittest suite'''

    suite = unittest.TestSuite()
    unittests.add_tests(suite)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    run_suite()
