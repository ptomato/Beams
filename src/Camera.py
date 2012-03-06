class CameraError(Exception):
    def __init__(self, msg, cam):
        self.msg = msg
        self.camera_number = cam

    def __str__(self):
        return '{0} on camera {1}'.format(self.msg, self.camera_number)

class Camera(object):
    def __init__(self, cam=-1):
        self.camera_number = cam
        self.frame = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()
        return False # don't suppress exceptions

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def query_frame(self):
        raise NotImplementedError()

    @property
    def id_string(self):
        raise NotImplementedError()

    @property
    def resolution(self):
        raise NotImplementedError()

    @property
    def roi(self):
        raise NotImplementedError()

    @roi.setter
    def roi(self, value):
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
