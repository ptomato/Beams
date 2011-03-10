import pygtk
pygtk.require20()
import gtk
import opencv
import Image

class CameraImage(gtk.Image):
    '''GTK widget for displaying images from the camera.'''

    def __init__(self):
        super(CameraImage, self).__init__()
        self._recording = False
        self._pil_image = None

    def take_snapshot(self):
        pass

    def set_recording(self, recording=True):
        self._recording = recording
        pass

#    def to_pixbuf(self):
#        '''Return the current PIL image as a GdkPixbuf.'''
#        try:
#            fd = StringIO.StringIO()
#            image.save(fd, 'ppm')
#            contents = fd.getvalue()
#        finally:
#            fd.close()
#        try:
#            loader = gtk.gdk.PixbufLoader('pnm')
#            loader.write(contents, len(contents))
#            pixbuf = loader.get_pixbuf()
#        finally:
#            loader.close()
#        return pixbuf
