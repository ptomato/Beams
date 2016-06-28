import cv2
from cv2.cv import CV_CAP_PROP_FRAME_WIDTH as FRAME_WIDTH
from cv2.cv import CV_CAP_PROP_FRAME_HEIGHT as FRAME_HEIGHT
from traitsui.api import Item, Label, RangeEditor, VGroup, View

from Camera import Camera, CameraError


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
        self._capture = cv2.VideoCapture(self.camera_number)

        # doesn't raise an exception on error, so we test it explicitly
        if not self._capture.isOpened():
            raise CameraError('Could not open camera', self.camera_number)

    def close(self):
        self._capture.release()

    def query_frame(self):
        success, frame = self._capture.read()
        if not success:
            raise CameraError('Could not query image', self.camera_number)
        self.frame = frame

    def _camera_number_changed(self, old, new):
        try:
            self.open()
        except CameraError:
            print 'Camera', new, 'was not found or could not be initialized.'
            print 'Changing back to camera', old, 'instead.'
            self.camera_number = old

    def _resolution_default(self):
        '''Resolution of the webcam - a 2-tuple'''
        width = self._capture.get(FRAME_WIDTH)
        height = self._capture.get(FRAME_HEIGHT)
        return (int(width), int(height))

    def _resolution_changed(self, value):
        width, height = value
        self._capture.set(FRAME_WIDTH, width)
        self._capture.set(FRAME_HEIGHT, height)
        if self._capture.get(FRAME_WIDTH) != width:
            raise CameraError('Width {0} not supported'.format(width), self.camera_number)
        if self._capture.get(FRAME_HEIGHT) != height:
            raise CameraError('Height {0} not supported'.format(height), self.camera_number)
