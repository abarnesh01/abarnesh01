import cv2
import threading
import time
from queue import Queue
from typing import Optional, Union
from loguru import logger

class CameraStream:
    """Threaded camera stream handler for RTSP and USB webcams."""

    def __init__(self, camera_id: str, source: Union[int, str], fps_limit: int = 30):
        self.camera_id = camera_id
        self.source = source
        self.fps_limit = fps_limit
        self.frame_delay = 1.0 / fps_limit
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_queue = Queue(maxsize=5)
        self.stopped = False
        self.thread: Optional[threading.Thread] = None
        
        self.is_connected = False
        self.last_reconnect_time = 0
        self.reconnect_interval = 5.0
        
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()

    def start(self):
        """Starts the capture thread."""
        self.stopped = False
        self.thread = threading.Thread(target=self._capture_loop, name=f"Stream-{self.camera_id}", daemon=True)
        self.thread.start()
        logger.info(f"Started camera stream: {self.camera_id}")
        return self

    def _connect(self):
        """Attempts to open the video source."""
        if self.cap is not None:
            self.cap.release()
            
        logger.info(f"Connecting to source: {self.source}")
        self.cap = cv2.VideoCapture(self.source)
        
        if self.cap.isOpened():
            self.is_connected = True
            logger.info(f"Successfully connected to {self.camera_id}")
        else:
            self.is_connected = False
            logger.error(f"Failed to connect to {self.camera_id}")

    def _capture_loop(self):
        """Internal loop for continuous frame capture."""
        self._connect()
        
        while not self.stopped:
            if not self.is_connected:
                current_time = time.time()
                if current_time - self.last_reconnect_time > self.reconnect_interval:
                    self.last_reconnect_time = current_time
                    self._connect()
                time.sleep(1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                logger.warning(f"Failed to read frame from {self.camera_id}. Attempting reconnect...")
                self.is_connected = False
                continue

            # Update FPS metrics
            self.frame_count += 1
            if time.time() - self.start_time >= 1.0:
                self.fps = self.frame_count / (time.time() - self.start_time)
                self.frame_count = 0
                self.start_time = time.time()

            # Maintain queue size by dropping old frames
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
            self.frame_queue.put(frame)
            
            # FPS Limiter
            time.sleep(self.frame_delay)

    def read(self) -> Optional[cv2.Mat]:
        """Returns the latest frame from the queue."""
        if self.frame_queue.empty():
            return None
        return self.frame_queue.get()

    def stop(self):
        """Stops the capture thread and releases resources."""
        self.stopped = True
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        logger.info(f"Stopped camera stream: {self.camera_id}")

    def get_status(self):
        return {
            "id": self.camera_id,
            "connected": self.is_connected,
            "fps": round(self.fps, 2),
            "queue_size": self.frame_queue.qsize()
        }
