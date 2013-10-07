import numpy as N
import VideoCapture

from Camera import Camera, CameraError


class DirectShow(Camera):
    '''Camera that interfaces through DirectShow'''

    def __init__(self, **traits):
        super(DirectShow, self).__init__(camera_number=0, **traits)
        self._cam = None

    def open(self):
        self._cam = VideoCapture.Device(self.camera_number)

        # Capture a throwaway frame in order to get the resolution
        # and bytes per pixel
        buffer, width, height = self._cam.getBuffer()
        self.resolution = (width, height)
        itemsize = len(buffer) / (width * height * 3)

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
        buffer, width, height = self._cam.getBuffer()
        self.resolution = (width, height)
        self.frame = N.ndarray(shape=(height, width, 3),
            buffer=buffer, dtype=self._dtype)

    def _id_string_default(self):
        try:
            return self._cam.getDisplayName() + ' (DirectShow driver)'
        except AttributeError:
            return 'DirectShow driver'

    def _resolution_changed(self, value):
        width, height = value
        self._cam.setResolution(width, height)

    def configure(self):
        self._cam.displayCaptureFilterProperties()
        self._cam.displayCapturePinProperties()
