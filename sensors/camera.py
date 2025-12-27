import cv2
import threading
import time
from core.time_utils import get_current_time_ms

class CameraStream:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(self.src)
        
        # Configure camera for higher FPS if possible, or standard request
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        self.grabbed, self.frame = self.cap.read()
        self.timestamp = get_current_time_ms()
        self.started = False
        self.read_lock = threading.Lock()
        
    def start(self):
        if self.started:
            print("[Camera] Already started.")
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        print("[Camera] Thread started.")
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame
                self.timestamp = get_current_time_ms()
            # Sleep slightly to avoid hogging CPU if camera is slow, 
            # but ideally we just block on read(). 
            # cv2.VideoCapture.read() blocks until a new frame is ready usually.
            
    def read(self):
        with self.read_lock:
            # return a copy to avoid threading issues if processing is slow?
            # actually for python frame is reference, so we should be careful. 
            # but for speed we return ref.
            return self.frame.copy() if self.frame is not None else None, self.timestamp

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()
        print("[Camera] Stopped.")

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
