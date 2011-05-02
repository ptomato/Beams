import gtk, gobject
import numpy as N
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg \
    import FigureCanvasGTKAgg as FigureCanvas

class CameraImage(FigureCanvas):
    
    def __init__(self):
        self._fig = Figure()
        FigureCanvas.__init__(self, self._fig)
        self._data = N.zeros((200, 320, 3), dtype=N.uint8)
        self._dims = self._data.shape
        
        # Draw the image
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._image = self._ax.imshow(self._data)
        self._ax.set_aspect('equal')
        self.draw()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # Convert to RGB data
        if len(value.shape) != 3:
            value = N.dstack((value, value, value))
        self._data = value
        self._display_data()

    def _display_data(self):
        if self._dims != self._data.shape:
            # Redraw the axes if the image is a different size
            self._fig.delaxes(self._ax)
            self._ax = self._fig.add_subplot(1, 1, 1)
            self._image = self._ax.imshow(self._data)
            self._dims = self._data.shape
        
        else:
            # Do it the fast way
            self._image.set_data(self._data)
        
        self._ax.set_aspect('equal')
        self.draw()
