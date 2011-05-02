import gtk, gobject
import numpy as N
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg \
    import FigureCanvasGTKAgg as FigureCanvas
import matplotlib.cm as CM

class CameraImage(FigureCanvas):
    
    def __init__(self):
        self._fig = Figure()
        FigureCanvas.__init__(self, self._fig)
        self._data = N.zeros((200, 320), dtype=N.uint8)
        self._dims = self._data.shape
        self._bw = (len(self._dims) == 2)
        self._cmap = CM.bone
        
        # Draw the image
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._image = self._ax.imshow(self._data, cmap=self._cmap)
        self._ax.set_aspect('equal')
        self.draw()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._display_data()

    def _display_data(self):
        if self._dims != self._data.shape:
            # Redraw the axes if the image is a different size
            self._fig.delaxes(self._ax)
            self._ax = self._fig.add_subplot(1, 1, 1)
            self._image = self._ax.imshow(self._data)
            self._dims = self._data.shape
            self._bw = (len(self._dims) == 2)
            if self._bw:
                if self._data.dtype == N.uint16:
                    self._image.set_clim(0, 65535)
                else:
                    self._image.set_clim(0, 255)
                self._image.set_cmap(self._cmap)
        
        else:
            # Do it the fast way
            self._image.set_data(self._data)
        
        self._ax.set_aspect('equal')
        self.draw()
