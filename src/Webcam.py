import cv

class Webcam:
	def __init__(self, cam=-1):
		self.capture = None
		self.camera_number = cam
	
	def __enter__(self):
		self.open()
		return self
	
	def __exit__(self):
		self.close()
	
	def open()
		self.capture = cv.CaptureFromCAM(self.camera_number)
	
	def close()
		cv.ReleaseCapture(self.capture)
	
	def query_frame()
		iplimage = cv.QueryFrame(self.capture)
		