import threading
import time

class ProcessingThread(threading.Thread):

    def __init__(self, controller, queue):
        super(ProcessingThread, self).__init__()
        self.abort_flag = False
        self.controller = controller
        self.queue = queue

    def run(self):
        while True:
            frame = self.queue.get()  # blocks until a frame is available
            if self.abort_flag:
                break

            # Do any transformations on the frame
            frame = self.controller.rotator.process_frame(frame)
            
            # Display the frame on screen
            self.controller.screen.data = frame

            # Send the frame to the analysis components
            self.controller.delta.process_frame(frame)
            self.controller.minmax.process_frame(frame)
            self.controller.profiler.process_frame(frame)

            time.sleep(0)
    
    def finish(self):
        """Signal the thread to stop."""
        self.abort_flag = True
        self.queue.put(None, block=False)
        # push fake data down the pipe in case it's waiting for data
