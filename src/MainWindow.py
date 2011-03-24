#!/usr/bin/env python

import sys
import gtk
import glib
import cv
import Image
import StringIO
from Webcam import *
import matplotlib.pyplot as P

class MainWindow:
    '''The main window for the LaserCam application.'''

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
        pass
    
    def action_take_video(self, action, data=None):
        pass
    
    def action_take_photo(self, action, data=None):
        pass
    
    def action_quit(self, action, data=None):
        gtk.main_quit()

    # Image capture timeout
    def image_capture(self):
        try:
            self.webcam.query_frame()
            #fig = P.figure()
            #ax = fig.add_subplot(1, 1, 1)
            #ax.imshow(self.webcam.frame)
            
            #fd = StringIO.StringIO()
            #fig.savefig(fd, format='png')
            
            pixbuf = gtk.gdk.pixbuf_new_from_data(self.webcam.frame.tostring(),
                gtk.gdk.COLORSPACE_RGB,
                has_alpha=False,
                bits_per_sample=8,
                width=self.webcam.frame.shape[1], 
                height=self.webcam.frame.shape[0],
                rowstride=self.webcam.frame.strides[0])
            #fd.close()
            self.screen.set_from_pixbuf(pixbuf)
                
        except WebcamError:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                flags=gtk.DIALOG_MODAL, 
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_CLOSE,
                message_format='No camera was detected. Did you forget to plug it in?')
            errmsg.run()
            sys.exit()
        
        while gtk.events_pending():
            gtk.main_iteration()
        
        return True  # keep the timeout going

    def __init__(self):
        # Load our user interface definition
        builder = gtk.Builder()
        builder.add_from_file('../data/LaserCam.ui')

        # Load our menu/toolbar definition
        manager = gtk.UIManager()
        manager.add_ui_from_file('../data/menus.xml')

        # Add all the actions to an action group for the menu and toolbar
        actiongroup = builder.get_object('actiongroup')
        actions = {
            'file_menu': '', 
            'edit_menu': '', 
            'view_menu': '', 
            'camera_menu': '', 
            'math_menu': '', 
            'help_menu': '',
            'about': '',
            'save': '<control>s',
            'take_video': '',
            'take_photo': '',
            'quit': '<control>q',
        }
        for action,accel in actions.iteritems():
            actiongroup.add_action_with_accel(builder.get_object(action), accel)
        manager.insert_action_group(actiongroup)

        # Build the window
        self.main_window = builder.get_object('main_window')
        self.main_window.get_child().pack_start(manager.get_widget('/menubar'), expand=False)
        self.main_window.get_child().pack_start(manager.get_widget('/toolbar'), expand=False)

        # Save pointers to other widgets
        self.about_window = builder.get_object('about_window')
        self.screen = builder.get_object('screen')

        builder.connect_signals(self, self)

        # Set up image capturing
        self.webcam = Webcam(0) # index of camera to be used
        try:
            self.webcam.open()
        except WebcamError:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                flags=gtk.DIALOG_MODAL, 
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_CLOSE,
                message_format='No camera was detected. Did you forget to plug it in?')
            errmsg.run()
            sys.exit()

        #self.image_capture()
        self.timeout_id = glib.timeout_add(50, self.image_capture)

if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.main_window.show_all()
    gtk.main()
