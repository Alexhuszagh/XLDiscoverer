'''
    Onstart/args
    ____________

    Argument parsers for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import argparse

# PARSER
# ------

PARSER = argparse.ArgumentParser()

# PUBLIC
# ------

PARSER.add_argument('-l', "--log",
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
                    default='INFO', help="Log level")
PARSER.add_argument('-r', "--remote-threshold",
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
                    default='ERROR', help="Threshold for remote Log level")
PARSER.add_argument('-o', "--stdout", action='store_false',
                    help="Remove stdout")
PARSER.add_argument('-e', "--stderr", action='store_false',
                    help="Remove stderr")

# DEBUGGING/INTERNAL
# ------------------

PARSER.add_argument('-d', "--debug", action='store_true',
                    help=argparse.SUPPRESS)
PARSER.add_argument('-t', "--trace", action='store_true',
                    help=argparse.SUPPRESS)
PARSER.add_argument('-p', "--pickle", action='store_true',
                    help=argparse.SUPPRESS)

# DEFINE LOCAL
# ------------

ARGS = PARSER.parse_args()

LOG = ARGS.log
REMOTE_THRESHOLD = ARGS.remote_threshold
STDOUT = ARGS.stdout
STDERR = ARGS.stderr
DEBUG = ARGS.debug
TRACE = ARGS.trace
PICKLE = ARGS.pickle

# CLEANUP
# -------

del argparse, ARGS, PARSER
