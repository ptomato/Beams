import gtk, gobject
import numpy as N

class ColorMapIndicator(gtk.DrawingArea):

    def __init__(self):
        gtk.DrawingArea.__gobject_init__(self)
        self._cmap = None
    
    @property
    def cmap(self):
        return self._cmap
    
    @cmap.setter
    def cmap(self, value):
        self._cmap = value
        self.queue_draw()
    
    def do_expose_event(self, event):
        if self._cmap is None:
            indices = [0] * 256
        else:
            cmap_array = N.array(self._cmap(N.arange(0, 256)) * 255, dtype=N.uint32)
            indices = list( cmap_array[:,0] << 16
                          | cmap_array[:,1] << 8
                          | cmap_array[:,2] )
        gc = self.window.new_gc()
        data = N.require(N.outer(N.ones(10), N.arange(0, 256, 2)),
               dtype=N.uint8,
               requirements=['C_CONTIGUOUS', 'ALIGNED'])
        self.window.draw_indexed_image(gc,
            0, 0,
            128, 10,
            gtk.gdk.RGB_DITHER_NONE,
            data, data.strides[0],
            indices)


gobject.type_register(ColorMapIndicator)