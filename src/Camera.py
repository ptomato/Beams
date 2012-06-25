from traits.api import HasTraits, Int, Str, Tuple, Array, Range


class CameraError(Exception):
    def __init__(self, msg, cam):
        self.msg = msg
        self.camera_number = cam

    def __str__(self):
        return '{0} on camera {1}'.format(self.msg, self.camera_number)


class Camera(HasTraits):
    camera_number = Int(-1)
    id_string = Str()
    resolution = Tuple(Int(), Int())
    roi = Tuple(Int(), Int(), Int(), Int())
    frame_rate = Range(1, 500, 30)
    frame = Array()

    def __init__(self, **traits):
        super(Camera, self).__init__(**traits)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()
        return False  # don't suppress exceptions

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def query_frame(self):
        raise NotImplementedError()

    def find_resolutions(self):
        '''
        Returns a list of resolution tuples that this camera supports.
        '''
        # Default: return the camera's own default resolution
        return [self.resolution]

    def configure(self):
        """Opens a dialog to set the camera's parameters."""
        pass
