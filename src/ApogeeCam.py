import numpy as N
import win32com.client
# generate and import apogee ActiveX module
win32com.client.gencache.EnsureModule('{A2882C73-7CFB-11D4-9155-0060676644C1}', 0, 1, 0)
from win32com.client import constants as Constants

from Camera import *

class ApogeeCam(Camera):
    '''Apogee Alta or Ascent camera'''
    
    def __init__(self, interface='usb', *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self._cam = win32com.client.Dispatch('Apogee.Camera2')
        if interface == 'usb':
            self._interface = Constants.Apn_Interface_USB
        elif interface == 'net':
            self._interface = Constants.Apn_Interface_NET
        else:
            raise ValueError('Invalid value "{0}" for interface; use "usb" or "net"'.format(interface))
        self._camera_num2 = 0
        self._buffer = None
    
    def open(self):
        self._cam.Init(self._interface, self.camera_number, self._camera_num2, 0)
        self._buffer = N.zeros(self.resolution, dtype=N.uint16)
    
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
        self._interface = discover.SelectedInterface
        self.camera_number = discover.SelectedCamIdOne
        self._camera_num2 = discover.SelectedCamIdTwo
    
    def reset(self):
        self._cam.ResetState()
        # if error status persists, raise an exception
        if self._cam.ImagingStatus < 0:
            raise CameraError('Error not cleared by reset', self.camera_number)
    
    @property
    def resolution(self):
        return self._cam.ImagingColumns, self._cam.ImagingRows
    
    @property
    def camera_model(self):
        return self._cam.CameraModel
    
    @property
    def driver_version(self):
        return self._cam.DriverVersion
