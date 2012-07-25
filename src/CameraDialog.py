import os.path
import imp
import glob
from traits.api import HasTraits, List, Tuple, Str, Int, Event
from traitsui.api import View, Item, CloseAction, Action, ListStrEditor, Handler
from traitsui.list_str_adapter import ListStrAdapter
from pyface.api import AboutDialog
from IconFinder import find_icon


class _CameraDescriptionAdapter(ListStrAdapter):
    def get_text(self, obj, trait, index):
        return ('{0[1]} - {0[2]}').format(getattr(obj, trait)[index])


class _CameraDialogHandler(Handler):
    # Signal handlers

    def on_about_plugin(self, info):
        # Find the selected plugin
        plugin_id = info.object.cameras[info.object.camera_selection][0]
        plugin_info = info.object.plugins[plugin_id]

        dialog = AboutDialog()
        dialog.additions = [
            plugin_info['name'],
            plugin_info['description'],
            'Copyright {copyright year} {author}'.format(**plugin_info)
        ]
        dialog.open()

    def _on_close(self, info):
        info.object.closed = True
        super(_CameraDialogHandler, self)._on_close(info)


class CameraDialog(HasTraits):
    """Dialog for selecting the camera plugin."""

    cameras = List(Tuple(Str, Str, Str))
    camera_selection = Int()
    closed = Event()

    # UI
    about_plugin = Action(name='About',
        action='on_about_plugin',
        icon=find_icon('about'))
    view = View(
        Item('cameras',
            show_label=False,
            editor=ListStrEditor(
                adapter=_CameraDescriptionAdapter(),
                selected_index='camera_selection',
                editable=False,
                multi_select=False)),
        buttons=[about_plugin, CloseAction],
        title='Available Camera Plugins',
        resizable=True,
        width=400,
        height=200,
        handler=_CameraDialogHandler())

    # Public

    def get_plugin_info(self):
        """For the selected plugin, returns a tuple of the module name to
        import and the class name to construct in order to get a Camera
        object."""

        # Find the selected plugin
        plugin_id = self.cameras[self.camera_selection][0]

        modulename = self.plugins[plugin_id]['module name']
        classname = self.plugins[plugin_id]['class name']
        return modulename, classname

    def __init__(self, **traits):
        super(CameraDialog, self).__init__(**traits)

        # Load the plugins
        self.plugins = {}
        for plugin_file in glob.glob('../plugins/*_plugin.py'):
            plugin_basename = os.path.split(plugin_file)[1]
            plugin_name = os.path.splitext(plugin_basename)[0]
            import_info = imp.find_module(plugin_name, ['../plugins'])
            plugin = imp.load_module(plugin_name, *import_info)
            self.plugins[plugin.info['id']] = plugin.info

        if 'dummy' not in self.plugins.keys():
            raise IOError("Plugin directory isn't configured properly")

        # Select the webcam
        try:
            self._select_plugin_by_name('webcam')
        except ValueError:
            assert 0, 'Webcam was not in list. Should not happen.'

    def _cameras_default(self):
        # Construct list store of plugins
        return [(self.plugins[plugin]['id'],
            self.plugins[plugin]['name'],
            self.plugins[plugin]['description'])
            for plugin in self.plugins.keys()]

    def _select_plugin_by_name(self, name):
        """Select a plugin by name"""
        for ix, cam in enumerate(self.cameras):
            if cam[0] == name:
                self.camera_selection = ix
                return
        raise ValueError('Plugin {} not in list'.format(name))

    def select_fallback(self):
        """Select the dummy plugin as a fallback"""
        try:
            self._select_plugin_by_name('dummy')
        except ValueError:
            assert 0, 'Dummy plugin was not in list. Should not happen.'

if __name__ == '__main__':
    CameraDialog().configure_traits()
