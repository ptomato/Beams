#!/usr/bin/env python

import sys
import Queue as queue  # in Python 3: import queue
from traits.api import HasTraits, Instance, DelegatesTo, Button, Enum, Str
from traitsui.api import (View, HSplit, Tabbed, HGroup, VGroup, Item, Label,
    MenuBar, ToolBar, Action, Menu, EnumEditor)
from pyface.api import MessageDialog
from chaco.api import gray, pink, jet

from Camera import Camera
from DummyGaussian import DummyGaussian
from MainHandler import MainHandler
from CameraImage import CameraImage, bone
from AwesomeColorMaps import awesome, isoluminant
from ColorMapEditor import ColorMapEditor
#from CameraDialog import *
from DeltaDetector import DeltaDetector
from MinMaxDisplay import MinMaxDisplay
from BeamProfiler import BeamProfiler
from Rotator import Rotator
from ProcessingThread import ProcessingThread
from AcquisitionThread import AcquisitionThread

ICON_PATH = '../icons/' # FIXME
MAX_QUEUE_SIZE = 0  # i.e. infinite

class MainWindow(HasTraits):
    '''The main window for the Beams application.'''

    # Current folder for file dialog
    _current_folder = None

    camera = Instance(Camera)
    id_string = DelegatesTo('camera')
    resolution = DelegatesTo('camera')
    frame_rate = DelegatesTo('camera')
    status = Str()
    screen = Instance(CameraImage)
    cmap = DelegatesTo('screen')
    delta = Instance(DeltaDetector)
    minmax = Instance(MinMaxDisplay)
    profiler = Instance(BeamProfiler)
    rotator = Instance(Rotator)
    acquisition_thread = Instance(AcquisitionThread)
    processing_thread = Instance(ProcessingThread)
    processing_queue = Instance(queue.Queue)

    # Actions
    about = Action(
        name='&About...',
        tooltip='About Beams',
        image=ICON_PATH + 'stock_about.png',
        action='action_about')
    save = Action(
        name='&Save Image',
        accelerator='Ctrl+S',
        tooltip='Save the current image to a file',
        image=ICON_PATH + 'stock_save.png',
        action='action_save')
    quit = Action(
        name='&Quit',
        accelerator='Ctrl+Q',
        tooltip='Exit the application',
        image=ICON_PATH + 'gtk-quit.png',
        action='_on_close')
    choose_camera = Action(
        name='Choose &Camera...',
        tooltip='Choose from a number of camera plugins',
        action='action_choose_camera')
    configure_camera = Action(
        name='Con&figure Camera...',
        tooltip='Open a dialog box to configure the camera. '
            'There may be no parameters available to configure.',
        image=ICON_PATH + 'stock_properties.png',
        action='action_configure_camera')
    find_resolution_action = Action(
        name='Find Resolution',
        tooltip='Look for the best resolution for the webcam',
        action='action_find_resolution')
    take_video = Action(
        name='Take &Video',
        style='toggle',
        tooltip='Start viewing the video feed from the camera',
        image=ICON_PATH + 'camera-video.png',
        action='action_take_video')
    take_photo = Action(
        name='Take &Photo',
        tooltip='Take one snapshot from the camera',
        image=ICON_PATH + 'camera-photo.png',
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
                        label='Camera'),
                    VGroup(
                        Item('cmap', label='Color scale',
                            editor=EnumEditor(values={
                                None: '0:None (image default)',
                                gray: '1:Grayscale',
                                bone: '2:Bone',
                                pink: '3:Copper',
                                jet:  '4:Rainbow (considered harmful)',
                                isoluminant: '5:Isoluminant',
                                awesome: '6:Low-intensity contrast'
                            })),
                        Item('screen', show_label=False,
                            editor=ColorMapEditor(width=256)),
                        label='Video'),
                    VGroup(
                        Item('rotator', style='custom', show_label=False),
                        label='Transform'),
                    VGroup(
                        Item('delta', style='custom', show_label=False),
                        Item('minmax', style='custom', show_label=False),
                        Item('profiler', style='custom', show_label=False),
                        label='Math'),
                    VGroup(label='Cross-section')),
                Item('screen', show_label=False, width=640, height=480,
                    style='custom')),
            Item('status', style='readonly', show_label=False)),
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
            Menu(about, name='&Help')),
        toolbar=ToolBar('|', save, '_', take_photo, take_video),
        title='Beams',
        resizable=True,
        handler=MainHandler)

    def _find_resolution_fired(self):
        return self.view.handler.action_find_resolution(None)
 
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

    def __init__(self, **traits):
        super(MainWindow, self).__init__(**traits)

        self.screen = CameraImage()

        # Build the camera selection dialog box
        #self.cameras_dialog = CameraDialog()
        #self.cameras_dialog.connect('response', self.on_cameras_response)

        # Build the plugin components
        self.profiler = BeamProfiler(screen=self.screen)
        self.minmax = MinMaxDisplay(screen=self.screen)
        self.delta = DeltaDetector(screen=self.screen)
        self.rotator = Rotator()

        # Open the default plugin
        #info = self.cameras_dialog.get_plugin_info()
        #try:
        #    self.select_plugin(*info)
        #except ImportError:
        #    # some module was not available, select the dummy
        #    self.cameras_dialog.select_fallback()
        #    info = self.cameras_dialog.get_plugin_info()
        #    self.select_plugin(*info)
        self.camera = DummyGaussian()
        
        self.processing_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self.acquisition_thread = None
        self.processing_thread = ProcessingThread(self, self.processing_queue)
        self.processing_thread.start()

if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.configure_traits()
