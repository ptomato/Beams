import cv
from cv import CV_CAP_PROP_FRAME_WIDTH as FRAME_WIDTH
from cv import CV_CAP_PROP_FRAME_HEIGHT as FRAME_HEIGHT
import numpy as N
from traitsui.api import Item, Label, RangeEditor, VGroup, View

from Camera import Camera, CameraError


def ipl2array(im):
    '''Converts an IplImage @im to a NumPy array.
    Adapted from http://opencv.willowgarage.com/wiki/PythonInterface'''
    depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

    a = N.fromstring(im.tostring(),
                     dtype=depth2dtype[im.depth],
                     count=im.width * im.height * im.nChannels)
    a.shape = (im.height, im.width, im.nChannels)
    return a


class Webcam(Camera):
    plugin_info = {
        'name': 'OpenCV',
        'description': 'Video camera interfacing through OpenCV',
        'author': 'Philip Chimento',
        'copyright year': '2011',
    }

    view = View(
        VGroup(
            Label('Select a different camera number if you\n'
                'have more than one webcam attached.\n'
                '-1 is the default camera.'),
            Item('camera_number',
                editor=RangeEditor(mode='spinner', low=-1, high=10)),
        ),
    )

    def __init__(self, **traits):
        super(Webcam, self).__init__(
            id_string='OpenCV driver, unknown camera',
            **traits)
        self._capture = None

    def open(self):
        self._capture = cv.CaptureFromCAM(self.camera_number)

        # doesn't raise an exception on error, so we test it explicitly
        iplimage = cv.QueryFrame(self._capture)
        if iplimage is None:
            raise CameraError('Could not query image', self.camera_number)

    def close(self):
        try:
            cv.ReleaseCapture(self._capture)
        except AttributeError:
            pass  # ReleaseCapture API was removed in later versions

    def query_frame(self):
        iplimage = cv.QueryFrame(self._capture)
        if iplimage is None:
            raise CameraError('Could not query image', self.camera_number)
        self.frame = ipl2array(iplimage)

    def _camera_number_changed(self, old, new):
        try:
            self.open()
        except CameraError:
            print 'Camera', new, 'was not found or could not be initialized.'
            print 'Changing back to camera', old, 'instead.'
            self.camera_number = old

    def _resolution_default(self):
        '''Resolution of the webcam - a 2-tuple'''
        width = cv.GetCaptureProperty(self._capture, FRAME_WIDTH)
        height = cv.GetCaptureProperty(self._capture, FRAME_HEIGHT)
        return (int(width), int(height))

    def _resolution_changed(self, value):
        width, height = value
        cv.SetCaptureProperty(self._capture, FRAME_WIDTH, width)
        cv.SetCaptureProperty(self._capture, FRAME_HEIGHT, height)
        if cv.GetCaptureProperty(self._capture, FRAME_WIDTH) != width:
            raise CameraError('Width {0} not supported'.format(width), self.camera_number)
        if cv.GetCaptureProperty(self._capture, FRAME_HEIGHT) != height:
            raise CameraError('Height {0} not supported'.format(height), self.camera_number)
