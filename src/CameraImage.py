import gtk, gobject
import numpy as N

class CameraImage(gtk.Image):
    
    __gproperties__ = {
        'data' : (gobject.TYPE_PYOBJECT,
            'Image data',
            'NumPy ndarray containing the data',
            gobject.PARAM_READWRITE)
    }
    
    def __init__(self):
        gtk.Image.__gobject_init__(self)
        self._data = N.zeros((200, 320, 3), dtype=N.uint8)
        self._display_data()
    
    def do_get_property(self, property):
        if property.name == 'data':
            return self._data
        else:
            raise AttributeError, 'unknown property %s' % property.name
    
    def do_set_property(self, property, value):
        if property.name == 'data':
            self._data = value
            self._display_data()
        else:
            raise AttributeError, 'unknown property %s' % property.name
            
    def _display_data(self):
        # OpenCV returns the camera data transposed
        pixbuf = gtk.gdk.pixbuf_new_from_data(self._data,
            gtk.gdk.COLORSPACE_RGB,
            has_alpha=False,
            bits_per_sample=8,
            width=self._data.shape[1],
            height=self._data.shape[0],
            rowstride=self._data.strides[0])
        self.set_from_pixbuf(pixbuf)
        
gobject.type_register(CameraImage)
