# coding: utf8
import scipy as S
import scipy.misc.pilutil
from traits.api import TraitError
from traitsui.api import Handler
from pyface.api import AboutDialog, FileDialog, OK

from AcquisitionThread import AcquisitionThread
from IconFinder import find_icon

class MainHandler(Handler):

    # Signal handlers
    def action_about(self, info):
        dialog = AboutDialog(image=find_icon('camera-video', size=64))
        dialog.additions = [
            'Beams 0.1',
            u'© 2010, 2011, 2012 P. F. Chimento',
            'MIT License'
        ]
        dialog.open()
    
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
        info.object.camera.configure_traits()

    def action_take_video(self, info):
        win = info.object
        if win.acquisition_thread is not None \
            and win.acquisition_thread.is_alive():
            win.acquisition_thread.abort_flag = True
        else:
            win.acquisition_thread = AcquisitionThread(camera=win.camera,
                queue=win.processing_queue)
            win.acquisition_thread.start()
    
    def action_take_photo(self, info):
        win = info.object
        win.camera.query_frame()
        win.processing_queue.put(win.camera.frame, block=False)
    
    def action_find_resolution(self, info):
        pass

    def closed(self, info, is_ok):
        win = info.object
        # Shut down the threads
        win.processing_thread.finish()
        win.processing_thread.join()
        if win.acquisition_thread is not None:
            win.acquisition_thread.abort_flag = True
            win.acquisition_thread.join()

        # Shut down the camera
        win.camera.close()

#    def on_cameras_response(self, dialog, response_id, data=None):
#        self.cameras_dialog.hide()
#        
#        if response_id == gtk.RESPONSE_CLOSE:
#            info = self.cameras_dialog.get_plugin_info()
#            self.select_plugin(*info)

#    # Select camera plugin
#    def select_plugin(self, module_name, class_name):
#        self._camera_module = __import__(module_name)
#        self._camera_class = getattr(self._camera_module, class_name)

#        # Set up image capturing
#        self.webcam = self._camera_class(cam=0) # index of camera to be used
#        try:
#            self.webcam.open()
#        except CameraError:
#            errmsg = gtk.MessageDialog(parent=self.main_window, 
#                flags=gtk.DIALOG_MODAL, 
#                type=gtk.MESSAGE_ERROR,
#                buttons=gtk.BUTTONS_CLOSE,
#                message_format='No camera was detected. Did you forget to plug it in?')
#            errmsg.run()
#            sys.exit()
#        
#        # Set up resolution box
#        self.resolutions.clear()
#        for (w, h) in self.webcam.find_resolutions():
#            it = self.resolutions.append(['{0} x {1}'.format(w, h), w, h])
#        self.resolution_box.props.active = 0

