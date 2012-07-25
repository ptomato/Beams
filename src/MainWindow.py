#!/usr/bin/env python
# coding: utf8

import sys
import Queue as queue  # in Python 3: import queue
from traits.api import (HasTraits, Instance, DelegatesTo, Button, Str, List,
    Range)
from traitsui.api import (View, HSplit, Tabbed, VGroup, Item, MenuBar,
    ToolBar, Action, Menu, EnumEditor, ListEditor, Group)
from pyface.api import error
from chaco.api import gray, pink, jet

from Camera import Camera, CameraError
from MainHandler import MainHandler
from CameraImage import CameraImage, bone
from AwesomeColorMaps import awesome, isoluminant
from ColorMapEditor import ColorMapEditor
from CameraDialog import CameraDialog
from DisplayPlugin import DisplayPlugin
from TransformPlugin import TransformPlugin
from ProcessingThread import ProcessingThread
from AcquisitionThread import AcquisitionThread
from IconFinder import find_icon

MAX_QUEUE_SIZE = 0  # i.e. infinite


class MainWindow(HasTraits):
    '''The main window for the Beams application.'''

    # Current folder for file dialog
    _current_folder = None

    camera = Instance(Camera)
    id_string = DelegatesTo('camera')
    resolution = DelegatesTo('camera')
    status = Str()
    screen = Instance(CameraImage, args=())
    cmap = DelegatesTo('screen')
    display_frame_rate = Range(1, 60, 15)
    transform_plugins = List(Instance(TransformPlugin))
    display_plugins = List(Instance(DisplayPlugin))
    acquisition_thread = Instance(AcquisitionThread)  # default: None
    processing_thread = Instance(ProcessingThread)  # default: None
    processing_queue = Instance(queue.Queue, kw={'maxsize': MAX_QUEUE_SIZE})
    cameras_dialog = Instance(CameraDialog, args=())

    # Actions
    about = Action(
        name='&About...',
        tooltip='About Beams',
        image=find_icon('about'),
        action='action_about')
    save = Action(
        name='&Save Image',
        accelerator='Ctrl+S',
        tooltip='Save the current image to a file',
        image=find_icon('save'),
        action='action_save')
    quit = Action(
        name='&Quit',
        accelerator='Ctrl+Q',
        tooltip='Exit the application',
        image=find_icon('quit'),
        action='_on_close')
    choose_camera = Action(
        name='Choose &Camera...',
        tooltip='Choose from a number of camera plugins',
        action='action_choose_camera')
    take_video = Action(
        name='Take &Video',
        style='toggle',
        tooltip='Start viewing the video feed from the camera',
        image=find_icon('camera-video'),
        action='action_take_video')
    take_photo = Action(
        name='Take &Photo',
        tooltip='Take one snapshot from the camera',
        image=find_icon('camera-photo'),
        action='action_take_photo',
        enabled_when='self.take_video.checked == False')

    find_resolution = Button()
    view = View(
        VGroup(
            HSplit(
                Tabbed(
                    VGroup(
                        Item('id_string', style='readonly', label='Camera'),
                        Item('resolution', style='readonly',
                            format_str=u'%i \N{multiplication sign} %i'),
                        Group(
                            Item('camera', show_label=False, style='custom'),
                            label='Camera properties',
                            show_border=True),
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
                        Item('display_frame_rate'),
                        label='Video'),
                    # FIXME: mutable=False means the items can't be deleted,
                    # added, or rearranged, but we do actually want them to
                    # be rearranged.
                    VGroup(Item('transform_plugins', show_label=False,
                        editor=ListEditor(style='custom', mutable=False)),
                        label='Transform'),
                    VGroup(Item('display_plugins', show_label=False,
                        editor=ListEditor(style='custom', mutable=False)),
                        label='Math')),
                Item('screen', show_label=False, width=640, height=480,
                    style='custom')),
            Item('status', style='readonly', show_label=False)),
        menubar=MenuBar(
            # vertical bar is undocumented but it seems to keep the menu
            # items in the order they were specified in
            Menu('|', save, '_', quit, name='&File'),
            Menu(name='&Edit'),
            Menu(name='&View'),
            Menu('|', choose_camera, '_', take_photo, take_video,
                name='&Camera'),
            Menu(name='&Math'),
            Menu(about, name='&Help')),
        toolbar=ToolBar('|', save, '_', take_photo, take_video),
        title='Beams',
        resizable=True,
        handler=MainHandler)

    def _find_resolution_fired(self):
        return self.view.handler.action_find_resolution(None)

    def _display_frame_rate_changed(self, value):
        self.processing_thread.update_frequency = value

    def _transform_plugins_default(self):
        plugins = []
        for name in ['Rotator', 'BackgroundSubtract']:
            module = __import__(name, globals(), locals(), [name])
            plugins.append(getattr(module, name)())
        return plugins

    def _display_plugins_default(self):
        plugins = []
        for name in ['BeamProfiler', 'MinMaxDisplay', 'DeltaDetector']:
            module = __import__(name, globals(), locals(), [name])
            plugins.append(getattr(module, name)(screen=self.screen))
        return plugins

    def __init__(self, **traits):
        super(MainWindow, self).__init__(**traits)

        # Build the camera selection dialog box
        self.cameras_dialog.on_trait_change(self.on_cameras_response, 'closed')

        # Open the default plugin
        info = self.cameras_dialog.get_plugin_info()
        try:
            self.select_plugin(*info)
        except ImportError:
            # some module was not available, select the dummy
            self.cameras_dialog.select_fallback()
            info = self.cameras_dialog.get_plugin_info()
            self.select_plugin(*info)

        self.processing_thread = ProcessingThread(self, self.processing_queue, self.display_frame_rate)
        self.processing_thread.start()

    def on_cameras_response(self):
        info = self.cameras_dialog.get_plugin_info()
        try:
            self.select_plugin(*info)
        except ImportError:
            error(None, 'Loading the {} camera plugin failed. '
                'Taking you back to the previous one.'.format(info[0]))
            self.cameras_dialog.select_fallback()
            info = self.cameras_dialog.get_plugin_info()
            self.select_plugin(*info)

    # Select camera plugin
    def select_plugin(self, module_name, class_name):
        self._camera_module = __import__(module_name)
        self._camera_class = getattr(self._camera_module, class_name)

        # Set up image capturing
        self.camera = self._camera_class()
        try:
            self.camera.open()
        except CameraError:
            error(None, 'No camera was detected. Did you forget to plug it in?')
            sys.exit()

if __name__ == '__main__':
    mainwin = MainWindow()
    mainwin.configure_traits()
