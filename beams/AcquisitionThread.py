import threading
import time


class AcquisitionThread(threading.Thread):

    def __init__(self, camera, queue):
        super(AcquisitionThread, self).__init__()
        self.abort_flag = False
        self.camera = camera
        self.queue = queue

    def run(self):
        while not self.abort_flag:
            self.camera.query_frame()
            self.queue.put(self.camera.frame, block=False)
            time.sleep(0)
