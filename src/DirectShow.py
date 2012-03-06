import numpy as N
import VideoCapture

from Camera import *

class DirectShow(Camera):
    '''Camera that interfaces through DirectShow'''
    
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self._cam = None
        self._width, self._height = (640, 480) # Uneducated guess
    
    def open(self):
        self._cam = VideoCapture.Device(self.camera_number)
        
        # Capture a throwaway frame in order to get the resolution
        # and bytes per pixel
        buffer, self._width, self._height = self._cam.getBuffer()
        itemsize = len(buffer) / (self._width * self._height * 3)
        
        # Pick an appropriate dtype and cache it
        if itemsize == 1:
            self._dtype = N.uint8
        elif itemsize == 2:
            self._dtype = N.uint16
        elif itemsize == 4:
            self._dtype = N.uint32
        else:
            raise CameraError(
                "Unsupported bytes per pixel '{}'".format(itemsize),
                self.camera_number)
    
    def close(self):
        # No other application can use the camera as long as the Device
        # object stays alive
        del self._cam
        self._cam = None
    
    def query_frame(self):
        buffer, self._width, self._height = self._cam.getBuffer()
        self.frame = N.ndarray(shape=(self._height, self._width, 3),
            buffer=buffer, dtype=self._dtype)
    
    @property
    def id_string(self):
        return self._cam.getDisplayName() + ' (DirectShow driver)'
    
    @property
    def resolution(self):
        return (self._width, self._height)
    
    @resolution.setter
    def resolution(self, value):
        width, height = value
        self._cam.setResolution(width, height)
    
    def configure(self):
        self._cam.displayCaptureFilterProperties()
        self._cam.displayCapturePinProperties()