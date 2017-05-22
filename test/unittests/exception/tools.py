'''
    Unittests/Exception/tools
    _________________________

    Unit tests for exception handlers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest
import warnings

from xldlib.exception import tools


# FUNCTIONS
# ---------


@tools.silence_warning(RuntimeWarning)
def silenced():
    '''Silenced RuntimeWarning which should not show on stack'''

    warnings.warn('Caught', RuntimeWarning, stacklevel=2)


@tools.except_error(AssertionError)
def except_error():
    '''Raise an AssertionError'''

    raise AssertionError


@tools.except_error(AssertionError, reraise=True)
def reraise_error():
    '''Raise an AssertionError'''

    raise AssertionError


@tools.except_error(AssertionError)
def exhaust_generator():
    '''Raise an AssertionError after partial evaluation of generator'''

    for item in range(10):
        assert item < 5
        yield item


# CASES
# -----


class ExceptionToolsTest(unittest.TestCase):
    '''Tests exception handlers for expected behavior'''

    def test_caught(self):
        '''Test an error is caught and excepted silently'''

        except_error()

    def test_generator(self):
        '''
        Test a generator function can be partially evaluated and
        silently caught.
        '''

        self.assertEquals(list(exhaust_generator()), list(range(5)))

    def test_raised(self):
        '''Test caught errors can be re-raised by keyword arguments'''

        with self.assertRaises(AssertionError):
            reraise_error()

    def test_silence_warning(self):
        '''Test warnings are caught and ignored by `tools.silence_warnings`'''

        with self.assertRaises(RuntimeWarning):
            with warnings.catch_warnings():
                warnings.simplefilter("error", category=RuntimeWarning)
                warnings.warn('Caught', RuntimeWarning, stacklevel=2)

        with warnings.catch_warnings():
            warnings.simplefilter("error", category=RuntimeWarning)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ExceptionToolsTest('test_caught'))
    suite.addTest(ExceptionToolsTest('test_generator'))
    suite.addTest(ExceptionToolsTest('test_raised'))
    suite.addTest(ExceptionToolsTest('test_silence_warning'))

