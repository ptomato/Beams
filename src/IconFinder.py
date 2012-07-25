import os.path
from pyface.api import ImageResource


def find_icon(icon_name, size=16):
    """
    Finds the icon named @icon_name, in the system icon theme directory if
    possible, and return it as an ImageResource.
    """

    possible_names = (
        icon_name + '.png',
        'stock_' + icon_name + '.png',
        'gtk-' + icon_name + '.png')
    # First try the system directory
    system_icon_path = '/Users/fliep/gtk/inst/share'  # os.getenv('XDG_DATA_DIRS')
    size_dir = '{0}x{0}'.format(size)
    if system_icon_path:
        for tryname in possible_names:
            icon_path = os.path.join(system_icon_path, 'icons', 'hicolor',
                'actions', size_dir, tryname)
            if os.path.exists(icon_path):
                return ImageResource(icon_path)
    # Next the application directory
    for tryname in possible_names:
        icon_path = os.path.join('..', 'icons', tryname)
        if os.path.exists(icon_path):
            return ImageResource(icon_path)
    # Next the current directory
    for tryname in possible_names:
        if os.path.exists(tryname):
            return ImageResource(tryname)
    raise IOError('Cannot find icon named "{}"'.format(icon_name))
