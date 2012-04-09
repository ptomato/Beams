from traits.api import TraitError
from traitsui.api import Handler
from pyface.api import FileDialog, OK

class MainHandler(Handler):

    # Signal handlers
    def action_about(self, info):
        pass  #self.about_window.present()
    
    def action_save(self, info):
        # First make a copy of the frame we will save
        save_frame = info.object.camera.frame.copy()
        
        # Then find out where to save it
        dialog = FileDialog(parent=info.object, action='save as', modal=True,
        	    title='Save Image')
        try:
            dialog.default_directory = info.object._current_folder
        except TraitError:
            pass   # thrown if _current_folder is None
        dialog.open()
        path = dialog.path
        
        # Store the directory for the next time
        info.object._current_folder = dialog.directory
        
        if dialog.return_code != OK:
            return
        
        # Default is PNG
        if '.' not in path:
            path += '.png'

        # Save it
        S.misc.imsave(path, save_frame)
    
    def action_choose_camera(self, info):
        pass # self.cameras_dialog.show()
    
    def action_configure_camera(self, info):
        info.object.camera.configure()

    def action_take_video(self, info):
        if not info.object.take_video.checked:
            pass #self.idle_id = glib.idle_add(self.image_capture)
        else:
            pass #glib.source_remove(self.idle_id)
    
    def action_take_photo(self, info):
        info.object.image_capture()
    
    def action_find_resolution(self, info):
        pass
    
    def action_quit(self, info):
        pass #gtk.main_quit()
    
#    def on_rotate_box_changed(self, combo, data=None):
#        self.screen.rotate = combo.props.active
#    
#    def on_detect_toggle_toggled(self, box, data=None):
#        self.delta.active = box.props.active

#    def on_minmax_toggle_toggled(self, box, data=None):
#        self.minmax.active = box.props.active

#    def on_profiler_toggle_toggled(self, box, data=None):
#        self.profiler.active = box.props.active
#    
#    def on_delta_threshold_value_changed(self, spin, data=None):
#        self.delta.threshold = spin.props.value

#    available_colormaps = {
#        0: None,
#        1: matplotlib.cm.gray,
#        2: matplotlib.cm.bone,
#        3: matplotlib.cm.pink,
#        4: matplotlib.cm.jet,
#        5: isoluminant,
#        6: awesome
#    }

#    def on_colorscale_box_changed(self, combo, data=None):
#        cmap_index = self.available_colormaps[combo.props.active]
#        self.screen.cmap = cmap_index
#        self.cmap_sample.cmap = cmap_index

#    def on_cameras_response(self, dialog, response_id, data=None):
#        self.cameras_dialog.hide()
#        
#        if response_id == gtk.RESPONSE_CLOSE:
#            info = self.cameras_dialog.get_plugin_info()
#            self.select_plugin(*info)
