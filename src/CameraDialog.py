import os.path
import imp
import glob
import gtk

class CameraDialog(gtk.Dialog):
    """Dialog for selecting the camera plugin."""
    
    # Public
    
    def get_plugin_info(self):
        """For the selected plugin, returns a tuple of the module name to
        import and the class name to construct in order to get a Camera
        object."""
        
        # Find the selected plugin
        model, iter = self.camera_selection.get_selected()
        plugin_id = model.get(iter, 0)[0]
        
        modulename = self.plugins[plugin_id]['module name']
        classname = self.plugins[plugin_id]['class name']
        return modulename, classname
    
    # Signal handlers

    def on_camera_about_clicked(self, button, *args):
        # Find the selected plugin
        model, iter = self.camera_selection.get_selected()
        plugin_id = model.get(iter, 0)[0]
        
        about = gtk.AboutDialog()
        about.props.program_name = self.plugins[plugin_id]['name']
        about.props.comments = self.plugins[plugin_id]['description']
        about.props.copyright = 'Copyright {copyright year} {author}'.format(**self.plugins[plugin_id])
        about.run()
        about.destroy()
    
    def format_camera_list(self, column, cell, model, iter, *args):
        cell.props.markup = ('<big><b>{0}</b></big>\n'
            '<i>{1}</i>').format(*model.get(iter, 1, 2))
    
    def __init__(self):
        gtk.Dialog.__init__(self,
            title='Available Camera Plugins',
            buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        
        # Load the plugins
        self.plugins = {}
        for plugin_file in glob.glob('../plugins/*_plugin.py'):
            plugin_basename = os.path.split(plugin_file)[1]
            plugin_name = os.path.splitext(plugin_basename)[0]
            import_info = imp.find_module(plugin_name, ['../plugins'])
            plugin = imp.load_module(plugin_name, *import_info)
            self.plugins[plugin.info['id']] = plugin.info
            
        if 'webcam' not in self.plugins.keys():
            raise IOError("Plugin directory isn't configured properly")
        
        # Construct list store of plugins
        self.cameras = gtk.ListStore(str, str, str)
        for plugin in self.plugins.keys():
            self.cameras.append(row=[
                self.plugins[plugin]['id'],
                self.plugins[plugin]['name'],
                self.plugins[plugin]['description']
            ])
        
        # Construct UI
        cameras_view = gtk.TreeView(model=self.cameras)
        cameras_view.props.headers_visible = False
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Plugins', renderer)
        column.set_cell_data_func(renderer, self.format_camera_list)
        cameras_view.append_column(column)
        cameras_view.set_size_request(250, 150)
        
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(cameras_view)
        scrolledwindow.show_all()
        
        about_button = gtk.Button(stock=gtk.STOCK_ABOUT)
        about_button.connect('clicked', self.on_camera_about_clicked)
        about_button.show()
        
        self.vbox.pack_start(scrolledwindow)
        self.vbox.pack_start(about_button, expand=False, fill=False, padding=6)
        
        self.camera_selection = cameras_view.get_selection()
        # Select the webcam
        iter = self.cameras.get_iter_first()
        while iter:
            if self.cameras.get_value(iter, 0) == 'webcam':
                break
            iter = self.cameras.iter_next(iter)
        else:
            assert 0, 'Webcam was not in list. Should not happen.'
        self.camera_selection.select_iter(iter)
    
