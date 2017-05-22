'''
    Unittests/Utils/logger
    ______________________

    Tests for XL Discoverer loggers, both to file and to stream.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules/submodules
import logging
import os
import sys
import unittest

from testfixtures import LogCapture, OutputCapture

from xldlib.utils import logger


# ITEMS
# -----

MESSAGES = (
    ('root', 'INFO', 'Some useful information'),
    ('root', 'WARNING', 'Some important warning'),
    ('root', 'ERROR', 'This is an error'),
    ('scans', 'INFO', 'This is another logger'),
    ('xlpy', 'ERROR', 'This is another logger'),
)

STREAMS = [
    'This is an error',
    'This is a message'
]

RECORDS = [
    'Initialized ',
    'Calling __call__ from ',
    'Traceback (most recent call last):',
    'Traceback (most recent call last)'
]

# OBJECTS
# -------


@logger.init('bio', 'INFO')
class CustomObject(object):
    '''Object with an initializer to log `__init__` and `__call__`'''

    def __init__(self):
        super(CustomObject, self).__init__()

    @logger.call('bio', 'info')
    def __call__(self):
        '''Empty call method'''

    @logger.raise_error
    def raised(self):
        '''Function which raises an error'''

        raise AssertionError

    @logger.except_error(AssertionError)
    def excepted(self):
        '''Function which raises (but is then excepted) for an error'''

        raise AssertionError


# CASES
# -----


class LoggerTest(unittest.TestCase):
    '''Tests loggers and decorators for expected log output'''

    def setUp(self):
        '''Set up unittests'''

        self.logger = logger.Logging(os.devnull, 'DEBUG')

    #     TESTS

    def test_logging(self):
        '''Test log formatters'''

        with LogCapture() as capture:
            for name, level, message in MESSAGES:
                log = logging.getLogger(name)
                getattr(log, level.lower())(message)

            capture.check(*MESSAGES)

    def test_streams(self):
        '''Test output to streams'''

        for stream, retain in [('stdout', False), ('stderr', True)]:
            self.logger.add_streaming('INFO', stream, retain=retain)
            with OutputCapture() as out:
                # the retain suppress the stdout, while keeping it does
                # not
                self.logger.add_streaming('INFO', stream, retain=retain)
                self._print_streams(getattr(sys, stream))

                if retain:
                    out.compare('\n'.join(STREAMS))
                else:
                    out.compare('')

    def test_decorators(self):
        '''Test decorators to log code progression'''

        with LogCapture() as capture:
            inst = CustomObject()
            inst()
            inst.excepted()

            with self.assertRaises(Exception):
                inst.raised()

            self.assertEquals(len(capture.records), 4)
            for expected, record in zip(RECORDS, capture.records):
                self.assertIn(expected, record.msg)

    #    NON-PUBLIC

    def _print_streams(self, buf):
        '''Print streams to a `buf`'''

        for message in STREAMS:
            print(message, file=buf)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(LoggerTest('test_logging'))
    suite.addTest(LoggerTest('test_streams'))
    suite.addTest(LoggerTest('test_decorators'))

