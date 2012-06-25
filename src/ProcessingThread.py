import threading
import time
from pyface.api import GUI


class ProcessingThread(threading.Thread):

    def __init__(self, controller, queue, update_frequency):
        super(ProcessingThread, self).__init__()
        self.abort_flag = False
        self.controller = controller
        self.queue = queue
        self.update_frequency = update_frequency

    def run(self):
        while True:
            frame = self.queue.get()  # blocks until a frame is available
            if self.abort_flag:
                break
            if self.queue.qsize() > 2:
                continue  # drop frame if there is a backlog

            # Do any transformations on the frame
            for plugin in self.controller.transform_plugins:
                frame = plugin.process_frame(frame)

            # Display the frame on screen
            GUI.set_trait_later(self.controller.screen, 'data', frame)

            # Send the frame to the analysis components
            for plugin in self.controller.display_plugins:
                plugin.process_frame(frame)

            time.sleep(1.0 / self.update_frequency)

    def finish(self):
        """Signal the thread to stop."""
        self.abort_flag = True
        self.queue.put(None, block=False)
        # push fake data down the pipe in case it's waiting for data
