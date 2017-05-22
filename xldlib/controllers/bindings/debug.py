'''
    Gui/Controllers/Bindings/debug
    ______________________________

    Functions which print stack traces and enter pdb.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules/submodules
import pdb
import sys
import traceback

from xldlib.utils import decorators


# DEBUGGING MODE
# --------------


@decorators.overloaded
def set_pdb_trace():
    '''Turn on the line-by-line debugger'''

    traceback.print_stack(file=sys.stdout)
    pdb.Pdb(stdout=sys.__stdout__).set_trace()



# TRACES
# ------


@decorators.overloaded
def trace_functions(frame, event):
    '''Traces function calls upon activation'''

    # skip non-call events
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        # Ignore write() calls from print statements
        return

    try:
        # grab file and line info, + caller
        func_line_no = frame.f_lineno
        func_filename = co.co_filename
        caller = frame.f_back
        caller_line_no = caller.f_lineno
        caller_filename = caller.f_code.co_filename
        print('Call to {0} on line {1} of {2} from line {3} of {4}'.format(
            func_name, func_line_no, func_filename,
            caller_line_no, caller_filename))

    except Exception:
        # Don't want to report any attribute errors from missing data in frames
        pass


@decorators.overloaded
def trace_lines(frame, event):
    '''Traces line-by-line within function calls'''

    # skip non-line events, such as calls
    if event != 'line':
        return

    try:
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        print('  %s line %s' % (func_name, line_no))

    except Exception:
        # Don't want to report any attribute errors from missing data in frames
        pass


@decorators.overloaded
def trace_both(frame, event):
    '''Traces both line-by-line and function call events'''

    if event == 'call':
        trace_functions(frame, event)
    elif event == 'line':
        trace_lines(frame, event)
