import numpy as N
import win32com.client
# generate and import apogee ActiveX module
win32com.client.gencache.EnsureModule('{A2882C73-7CFB-11D4-9155-0060676644C1}', 0, 1, 0)
from win32com.client import constants as Constants
from traits.api import Str, Int, Enum

from Camera import *

_interface_constants = {
    'usb': Constants.Apn_Interface_USB,
    'net': Constants.Apn_Interface_NET}
_reverse_constants = dict((v, k) for k, v in _interface_constants.iteritems())


class ApogeeCam(Camera):
    '''Apogee Alta or Ascent camera'''

    camera_num2 = Int(0)
    camera_model = Str()
    driver_version = Str()
    interface = Enum('usb', 'net')

    def __init__(self, **traits):
        super(ApogeeCam, self).__init__(camera_number=0, **traits)
        self._cam = win32com.client.Dispatch('Apogee.Camera2')
        self._buffer = None

    def open(self):
        self._cam.Init(_interface_constants[self.interface], self.camera_number,
            self.camera_num2, 0)
        self._buffer = N.zeros(self.roi[-1:-3:-1], dtype=N.uint16)

    def close(self):
        self._cam.Close()

    def query_frame(self, expose_time=0.05, open_shutter=True):
        try:
            self._cam.Expose(expose_time, open_shutter)
            while self._cam.ImagingStatus != Constants.Apn_Status_ImageReady:
                pass
            self._cam.GetImage(self._buffer.ctypes.data)
        finally:
            if self._cam.ImagingStatus < 0:
                self.reset()
        self.frame = N.copy(self._buffer)

    def choose_camera(self):
        discover = win32com.client.Dispatch('Apogee.CamDiscover')
        discover.DlgCheckUsb = True
        discover.ShowDialog(True)
        if not discover.ValidSelection:
            raise ValueError('No camera selected')
        self.interface = _reverse_constants[discover.SelectedInterface]
        self.camera_number = discover.SelectedCamIdOne
        self.camera_num2 = discover.SelectedCamIdTwo

    def reset(self):
        self._cam.ResetState()
        # if error status persists, raise an exception
        if self._cam.ImagingStatus < 0:
            raise CameraError('Error not cleared by reset', self.camera_number)

    def _resolution_default(self):
        return self._cam.ImagingColumns, self._cam.ImagingRows

    def _camera_model_default(self):
        return self._cam.CameraModel

    def _driver_version_default(self):
        return self._cam.DriverVersion

    def _id_string_default(self):
        return 'Apogee {} Driver version: {}'.format(
            self.camera_model,
            self.driver_version)

    def _roi_default(self):
        return (self._cam.RoiStartX,
            self._cam.RoiStartY,
            self._cam.RoiPixelsH,
            self._cam.RoiPixelsV)

    def _roi_changed(self, value):
        x, y, w, h = value
        self._cam.RoiStartX = x
        self._cam.RoiStartY = y
        self._cam.RoiPixelsH = w
        self._cam.RoiPixelsV = h
        self._buffer = N.zeros((h, w), dtype=N.uint16)
