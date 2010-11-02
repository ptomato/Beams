#!/usr/bin/env python

import sys
import gtk
import glib
import cv
import Image
import StringIO

# Helper functions
def pil_image_to_pixbuf(image):
    try:
        fd = StringIO.StringIO()
        image.save(fd, 'ppm')
        contents = fd.getvalue()
    finally:
        fd.close()
    try:
        loader = gtk.gdk.PixbufLoader('pnm')
        loader.write(contents, len(contents))
        pixbuf = loader.get_pixbuf()
    finally:
        loader.close()
    return pixbuf

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
    
    # Image capture timeout
    def image_capture(self):
        self.current_image = cv.QueryFrame(self.capture)
        try:
            pilimage = Image.fromstring('L', cv.GetSize(self.current_image), 
                                        self.current_image.tostring())
            self.screen.set_from_pixbuf(pil_image_to_pixbuf(pilimage))
        except cv.error:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                                       flags=gtk.DIALOG_MODAL, 
                                       type=gtk.MESSAGE_ERROR,
                                       buttons=gtk.BUTTONS_CLOSE,
                                       message_format='There was an error '
                                       'reading the camera.')
            errmsg.run()
            return False  # stop the timeout function
        return True
    
    def __init__(self):
    	# Load our user interface definition
        builder = gtk.Builder()
        builder.add_from_file('../data/LaserCam.ui')
        
        # Load our menu/toolbar definition
        manager = gtk.UIManager()
        manager.add_ui_from_file('../data/menus.xml')
        
        # Add all the actions to an action group for the menu and toolbar
        actiongroup = builder.get_object('actiongroup')
        actions = {'file_menu': '', 
                   'edit_menu': '', 
                   'view_menu': '', 
                   'camera_menu': '', 
                   'math_menu': '', 
                   'help_menu': '',
                   'about': ''}
        for action,accel in actions.iteritems():
            actiongroup.add_action_with_accel(builder.get_object(action), accel)
        manager.insert_action_group(actiongroup)
        
        # Build the window
        self.main_window = builder.get_object('main_window')
        self.main_window.get_child().pack_start(manager.get_widget('/menubar'), 
                                                expand=False)
        self.main_window.get_child().pack_start(manager.get_widget('/toolbar'), 
                                                expand=False)
        
        # Save pointers to other widgets
        self.about_window = builder.get_object('about_window')
        self.screen = builder.get_object('screen')

        builder.connect_signals(self, self)
        
        # Set up image capturing
        self.capture = cv.CaptureFromCAM(0) # index of camera to be used
        # doesn't raise an exception on failure, so we test it explicitly
        self.current_image = cv.QueryFrame(self.capture);
        if self.current_image is None:
            errmsg = gtk.MessageDialog(parent=self.main_window, 
                                       flags=gtk.DIALOG_MODAL, 
                                       type=gtk.MESSAGE_ERROR,
                                       buttons=gtk.BUTTONS_CLOSE,
                                       message_format='No camera was detected. '
                                       'Did you forget to plug it in?')
            errmsg.run()
            sys.exit()
        
        #self.timeout_id = glib.timeout_add(50, self.image_capture)
        
if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.main_window.show_all()
    gtk.main()

