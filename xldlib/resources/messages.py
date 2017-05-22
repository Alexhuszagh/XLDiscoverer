'''
    Resources/other/messages
    ________________________

    Text-based messages to display on views.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import version

__all__ = [
    'ABRIDGED_LICENSE',
    'MESSAGES',
]


# MESSAGES
# --------

MESSAGES = {
    'update': {
        'windowTitle': "Update XL Toolset",
        'text': ("Version {0} is now available for download.\nYou "
                 "are currently using version %s.\nWould "
                 "you like to update XL Discoverer?" % version.BUILD)
    },
    'send_logs': {
        'windowTitle': "Send Anonymous Logs",
        'text': ("Would you like to send anonymous logs to aid XL "
                 "Discoverer development and bug fixes?")
    },
    'no_worker': {
        'windowTitle': "Download Error",
        'text': ("Sorry, no compiled binaries were found"
                 "for your system architecture.")
    }
}


ABRIDGED_LICENSE = '''
Copyright (C) 2015 The Regents of the University of California.

xlDiscoverer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This xlDiscoverer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xlDiscoverer.  If not, see <http://www.gnu.org/licenses/>.
'''
