#!/usr/bin/env python

import sys
import gtk
import glib
import scipy as S
import scipy.misc.pilutil
import matplotlib.cm

from ApogeeCam import *
from Webcam import *
from CameraImage import *
from AwesomeColorMaps import awesome, isoluminant
from ColorMapIndicator import *

class MainWindow:
    '''The main window for the LaserCam application.'''

    # Current folder for file dialog
    _current_folder = None

    # Wrappers for C signal handlers called from gtk.Builder
    def gtk_widget_hide(self, widget, *args):
        widget.hide()

    def gtk_widget_hide_on_delete(self, widget, *args):
        return widget.hide_on_delete()

    def gtk_main_quit_on_delete(self, widget, *args):
        gtk.main_quit()
        return False

    # Signal handlers
    def action_about(self, action, data=None):
        self.about_window.present()
    
    def action_save(self, action, data=None):
        # First make a copy of the frame we will save
        save_frame = self.webcam.frame.copy()
        
        # Then find out where to save it
        dialog = gtk.FileChooserDialog('Save Image', self.main_window,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        try:
            dialog.set_current_folder(self._current_folder)
        except TypeError:
            pass  # thrown if current folder is None
        response = dialog.run()
        path = dialog.get_filename()
        
        # Store the directory for the next time
        self._current_folder = dialog.get_current_folder()
        
        dialog.destroy()
        if response != gtk.RESPONSE_ACCEPT:
            return
        
        # Save it
        S.misc.imsave(path, save_frame)
    
    def action_find_resolution(self, action, data=None):
        pass
    
    def action_take_video(self, action, data=None):
        # Set the 'Take Photo' action insensitive if 'Take Video' is on
        self.actiongroup.get_action('take_photo').set_sensitive(not action.get_active())
        
        if action.get_active():
            self.idle_id = glib.idle_add(self.image_capture)
        else:
            glib.source_remove(self.idle_id)
    
    def action_take_photo(self, action, data=None):
        self.image_capture()
    
    def action_quit(self, action, data=None):
        gtk.main_quit()
    
    def on_rotate_box_changed(self, combo, data=None):
        self.screen.rotate = combo.props.active

    available_colormaps = {
        0: None,
        1: matplotlib.cm.gray,
        2: matplotlib.cm.bone,
        3: matplotlib.cm.pink,
        4: matplotlib.cm.jet,
        5: isoluminant,
        6: awesome
    }

    def on_colorscale_box_changed(self, combo, data=None):
        cmap_index = self.available_colormaps[combo.props.active]
        self.screen.cmap = cmap_index
        self.cmap_sample.cmap = cmap_index

    # Image capture timeout
    def image_capture(self):
        try:
            self.webcam.query_frame()
        except CameraError:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                flags=gtk.DIALOG_MODAL, 
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_CLOSE,
                message_format='There was an error reading from the camera.')
            errmsg.run()
            sys.exit()
            
        self.screen.data = self.webcam.frame
        return True  # keep the idle function going

    def __init__(self):
        # Load our user interface definition
        builder = gtk.Builder()
        builder.add_from_file('../data/LaserCam.ui')

        # Load our menu/toolbar definition
        manager = gtk.UIManager()
        manager.add_ui_from_file('../data/menus.xml')

        # Add all the actions to an action group for the menu and toolbar
        self.actiongroup = builder.get_object('actiongroup')
        actions = {
            'file_menu': '', 
            'edit_menu': '', 
            'view_menu': '', 
            'camera_menu': '', 
            'math_menu': '', 
            'help_menu': '',
            'about': '',
            'save': '<control>s',
            'find_resolution': '',
            'take_video': '',
            'take_photo': '',
            'quit': '<control>q',
        }
        for action,accel in actions.iteritems():
            self.actiongroup.add_action_with_accel(builder.get_object(action), accel)
        manager.insert_action_group(self.actiongroup)

        # Build the window
        self.main_window = builder.get_object('main_window')
        self.main_window.get_child().pack_start(manager.get_widget('/menubar'), expand=False)
        self.main_window.get_child().pack_start(manager.get_widget('/toolbar'), expand=False)
        
        self.screen = CameraImage()
        self.screen.set_size_request(640, 480)
        self.main_window.get_child().pack_start(self.screen)
        
        self.cmap_sample = ColorMapIndicator()
        self.cmap_sample.set_size_request(128, 10)
        builder.get_object('table2').attach(self.cmap_sample, 2, 3, 2, 3,
            xoptions=0, yoptions=0)

        # Save pointers to other widgets
        self.about_window = builder.get_object('about_window')
        self.colorscale_box = builder.get_object('colorscale_box')
        self.resolution_box = builder.get_object('resolution_box')
        self.resolutions = builder.get_object('resolutions')

        # Set up image capturing
        self.webcam = Webcam(cam=0) # index of camera to be used
        try:
            self.webcam.open()
        except CameraError:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                flags=gtk.DIALOG_MODAL, 
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_CLOSE,
                message_format='No camera was detected. Did you forget to plug it in?')
            errmsg.run()
            sys.exit()
            
        # Set up resolution box
        for (w, h) in self.webcam.find_resolutions():
            it = self.resolutions.append(['{0} x {1}'.format(w, h), w, h])
        self.resolution_box.props.active = 0

        # Connect the signals last of all
        builder.connect_signals(self, self)

if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.main_window.show_all()
    gtk.main()
