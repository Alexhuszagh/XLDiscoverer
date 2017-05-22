'''
    Resources/Qt/images
    ___________________

    Loads the image library into memory.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from PySide import QtGui

from xldlib.resources import paths


__all__ = [
    'IMAGES'
]


# PUBLIC
# ------


def load_images(images=None, names=None):
    '''Load QPixmaps from PNG files. See argspec in `_load_images`'''

    if images is None:
        images = {}
    if names is None:
        names = IMAGE_NAMES
    return _load_images(images, names)


# NON-PUBLIC
# ----------


def _load_images(images, names):
    '''
    Find PNG files from a name identifier, and store generated pixmaps
    into the `images` holder.

    Args:
        images (dict): {name: pixmap} image holder
        names (iterable): names of images to load
    '''

    for name in names:
        path = os.path.join(paths.DIRS['png'], name + '.png')
        if os.path.exists(path):
            pixmap = QtGui.QPixmap(path)
            images[name] = QtGui.QIcon(pixmap)

        else:
            raise OSError("Cannot find path: {}".format(path))

    return images


# DATA
# ----

IMAGE_NAMES = (
    # Embedded
    'red_dot',
    'green_dot',
    'orange_dot',
    'disc',
    'circle',

    # Tray Icons
    'splash_icon',
    'xldiscoverer_icon',
    'quantitative_xldiscoverer_icon',
    'transition_icon',
    'fingerprint_icon',

    # Banners
    'banner',
    'xldiscoverer_banner',
    'quantitative_xldiscoverer_banner',

    # Splash Menu
    'xldiscoverer_menu',
    'quantitative_xldiscoverer_menu',
    'fingerprint_menu',
    'transition_menu',

    # CrossLink Discoverer Menu
    'input_files_menu',
    'labeling_menu',
    'crosslinkers_menu',
    'proteins_menu',
    'settings_menu',

    # Run summary icons
    'save_session_icon',
    'save_openoffice_icon',
    'save_transitions_icon',
    'save_fingerprinting_icon',

    # Settings
    'folder_icon',

    # Toolbar
    'home',
    'next',
    'previous',
    'zoomin',
    'zoomout',

    # Keyboard
    'keyboard-a',
    'keyboard-b',
    'keyboard-c',
    'keyboard-d',
    'keyboard-e',
    'keyboard-f',
    'keyboard-g',
    'keyboard-h',
    'keyboard-i',
    'keyboard-j',
    'keyboard-k',
    'keyboard-l',
    'keyboard-m',
    'keyboard-n',
    'keyboard-o',
    'keyboard-p',
    'keyboard-q',
    'keyboard-r',
    'keyboard-s',
    'keyboard-t',
    'keyboard-u',
    'keyboard-v',
    'keyboard-w',
    'keyboard-x',
    'keyboard-y',
    'keyboard-z',
    'keyboard-left',
    'keyboard-right',
    'keyboard-up',
    'keyboard-down',
    'keyboard-delete',
    'keyboard-space',
    'keyboard-enter'
)

IMAGES = load_images()
