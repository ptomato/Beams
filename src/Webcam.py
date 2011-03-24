import cv
import numpy as N

class WebcamError(Exception):
	def __init__(self, msg, cam):
		self.msg = msg
		self.camera_number = cam
	
	def __str__(self):
		return '{0} on camera {1}'.format(self.msg, self.camera_number)

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

class Webcam:
	def __init__(self, cam=-1):
		self._capture = None
		self.camera_number = cam
		self.frame = None
	
	def __enter__(self):
		self.open()
		return self
	
	def __exit__(self):
		self.close()
	
	def open(self):
		self._capture = cv.CaptureFromCAM(self.camera_number)
		
		# doesn't raise an exception on error, so we test it explicitly
		iplimage = cv.QueryFrame(self._capture)
		if iplimage is None:
			raise WebcamError('Could not query image', self.camera_number)
	
	def close(self):
		cv.ReleaseCapture(self._capture)
	
	def query_frame(self):
		iplimage = cv.QueryFrame(self._capture)
		if iplimage is None:
			raise WebcamError('Could not query image', self.camera_number)
		
		rgb = ipl2array(iplimage)
		
		# Standard NTSC conversion formula
		#self.frame = N.array((0.2989 * rgb[... ,0] 
		#		   + 0.5870 * rgb[..., 1]
		#		   + 0.1140 * rgb[..., 2]), dtype=N.uint8)
		self.frame = rgb
