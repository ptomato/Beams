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

    def __exit__(self, type, value, traceback):
        self.close()
        return False # don't suppress exceptions

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def query_frame(self):
        raise NotImplementedError()

    @property
    def resolution(self):
        raise NotImplementedError()
