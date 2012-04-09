#!/usr/bin/env python

#import sys
#import scipy as S
#import scipy.misc.pilutil
#import matplotlib.cm
from traits.api import HasTraits, Instance, DelegatesTo, Button, Enum, Str
from traitsui.api import (View, HSplit, Tabbed, HGroup, VGroup, Item, Label,
    MenuBar, ToolBar, Action, Menu)

from Camera import *
from DummyGaussian import *
from MainHandler import *
#from CameraImage import *
#from AwesomeColorMaps import awesome, isoluminant
#from ColorMapIndicator import *
#from CameraDialog import *
#from DeltaDetector import *
#from MinMaxDisplay import *
#from BeamProfiler import *

class MainWindow(HasTraits):
    '''The main window for the Beams application.'''

    # Current folder for file dialog
    _current_folder = None

    camera = Instance(Camera)
    id_string = DelegatesTo('camera')
    resolution = DelegatesTo('camera')
    frame_rate = DelegatesTo('camera')
    color_scale = Enum('a', 'b')
    rotation_angle = Enum(0, 90, 180, 270)
    status = Str()

    # Actions
    about = Action(
        name='&About...',
        tooltip='About Beams',
        action='action_about')
    save = Action(
        name='&Save Image',
        accelerator='Ctrl+S',
        tooltip='Save the current image to a file',
        action='action_save')
    quit = Action(
        name='&Quit',
        accelerator='Ctrl+Q',
        tooltip='Exit the application',
        action='action_quit')
    choose_camera = Action(
        name='Choose &Camera...',
        tooltip='Choose from a number of camera plugins',
        action='action_choose_camera')
    configure_camera = Action(
        name='Con&figure Camera...',
        tooltip='Open a dialog box to configure the camera. '
            'There may be no parameters available to configure.',
        action='action_configure_camera')
    find_resolution_action = Action(
        name='Find Resolution',
        tooltip='Look for the best resolution for the webcam',
        action='action_find_resolution')
    take_video = Action(
        name='Take &Video',
        style='toggle',
        tooltip='Start viewing the video feed from the camera',
        action='action_take_video')
    take_photo = Action(
        name='Take &Photo',
        tooltip='Take one snapshot from the camera',
        action='action_take_photo',
        enabled_when='self.take_video.checked == False')

    find_resolution = Button()
    view = View(
        VGroup(
            HSplit(
                Tabbed(
                    VGroup(
                        Item('id_string', style='readonly', label='Camera'),
                        HGroup(
                            Item('resolution'),
                            Item('find_resolution', show_label=False)),
                        HGroup(
                            Item('frame_rate', style='custom'),
                            Label('fps')),
                        label='Camera'
                    ),
                    VGroup(
                        Item('color_scale'),
                        label='Video'
                    ),
                    VGroup(
                        Item('rotation_angle'),
                        label='Transform'
                    ),
                    VGroup(label='Math'),
                    VGroup(label='Cross-section')
                )
            ),
            Item('status', style='readonly', show_label=False)
        ),
        menubar=MenuBar(
            Menu(save, '_', quit, name='&File'),
            Menu(name='&Edit'),
            Menu(name='&View'),
            Menu('|',
                # vertical bar is undocumented but it seems to keep the menu
                # items in the order they were specified in
                choose_camera, configure_camera, find_resolution_action, '_',
                take_photo, take_video,
                name='&Camera'),
            Menu(name='&Math'),
            Menu(about, name='&Help')
        ),
        toolbar=ToolBar('|', save, '_', take_photo, take_video),
        title='Beams',
        resizable=True,
        handler=MainHandler
    )

    def __init__(self):
        self.camera = DummyGaussian()

    def _find_resolution_fired(self):
        return self.view.handler.action_find_resolution(None)
#    
#    # Image capture timeout
#    def image_capture(self):
#        try:
#            self.webcam.query_frame()
#        except CameraError:
#            errmsg = gtk.MessageDialog(parent=self.main_window, 
#                flags=gtk.DIALOG_MODAL, 
#                type=gtk.MESSAGE_ERROR,
#                buttons=gtk.BUTTONS_CLOSE,
#                message_format='There was an error reading from the camera.')
#            errmsg.run()
#            sys.exit()
#            
#        self.screen.data = self.webcam.frame
#        
#        # Send the frame to the processing components
#        if self.delta.active:
#            self.delta.send_frame(self.webcam.frame)
#        if self.minmax.active:
#            self.minmax.send_frame(self.webcam.frame)
#        if self.profiler.active:
#            self.profiler.send_frame(self.webcam.frame)

#        return True  # keep the idle function going
#    
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
#        
#        # Change camera info label
#        self.camera_label.props.label = \
#            'Camera: {}'.format(self.webcam.id_string)

#    def __init__(self):
#        # Load our user interface definition
#        builder = gtk.Builder()
#        builder.add_from_file('../data/Beams.ui')

#        # Load our menu/toolbar definition
#        manager = gtk.UIManager()
#        manager.add_ui_from_file('../data/menus.xml')

#        # Add all the actions to an action group for the menu and toolbar
#        self.actiongroup = builder.get_object('actiongroup')
#        manager.insert_action_group(self.actiongroup)

#        # Build the window
#        self.main_window = builder.get_object('main_window')
#        self.main_window.get_child().pack_start(manager.get_widget('/menubar'), expand=False)
#        self.main_window.get_child().pack_start(manager.get_widget('/toolbar'), expand=False)
#        
#        self.screen = CameraImage()
#        self.screen.set_size_request(640, 480)
#        builder.get_object('main_hbox').pack_start(self.screen)
#        
#        self.cmap_sample = ColorMapIndicator()
#        self.cmap_sample.set_size_request(128, 10)
#        builder.get_object('colorscale_vbox').pack_start(self.cmap_sample)

#        # Build the camera selection dialog box
#        self.cameras_dialog = CameraDialog()
#        self.cameras_dialog.connect('response', self.on_cameras_response)
#        
#        # Build the beam profiler
#        self.profiler = BeamProfiler(self.screen)
#        builder.get_object('profiler_toggle').props.active = self.profiler.active

#        # Build the min-max display
#        self.minmax = MinMaxDisplay(self.screen)
#        builder.get_object('minmax_toggle').props.active = self.minmax.active

#        # Build the delta detector
#        self.delta = DeltaDetector(self.screen)
#        builder.get_object('detect_toggle').props.active = self.delta.active
#        builder.get_object('delta_threshold').props.value = self.delta.threshold

#        # Save pointers to other widgets
#        self.about_window = builder.get_object('about_window')
#        self.colorscale_box = builder.get_object('colorscale_box')
#        self.resolution_box = builder.get_object('resolution_box')
#        self.resolutions = builder.get_object('resolutions')
#        self.camera_label = builder.get_object('camera_label')
#        self.current_delta = builder.get_object('current_delta')

#        # Open the default plugin
#        info = self.cameras_dialog.get_plugin_info()
#        try:
#            self.select_plugin(*info)
#        except ImportError:
#            # some module was not available, select the dummy
#            self.cameras_dialog.select_fallback()
#            info = self.cameras_dialog.get_plugin_info()
#            self.select_plugin(*info)

#        # Connect the signals last of all
#        builder.connect_signals(self, self)

if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.configure_traits()
