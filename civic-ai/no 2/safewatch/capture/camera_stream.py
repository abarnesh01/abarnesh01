import cv2
import threading
import time
from loguru import logger
from typing import Optional, Tuple
from queue import Queue

class CameraStream:
    """
    High-performance camera stream handler using threading for non-blocking frame capture.
    Supports RTSP, USB webcams, and reconnection logic.
    """
    def __init__(self, camera_id: int, name: str, source: str, fps_limit: int = 30):
        self.camera_id = camera_id
        self.name = name
        self.source = source if not str(source).isdigit() else int(source)
        self.fps_limit = fps_limit
        
        self.cap = None
        self.frame_queue = Queue(maxsize=5)
        self.stopped = False
        self.connected = False
        self.fps = 0
        self.last_reconnect_time = 0
        
        # Performance monitoring
        self.frame_count = 0
        self.start_time = time.time()
        
        self.thread = threading.Thread(target=self._update, name=f"CameraStream-{name}", daemon=True)

    def start(self):
        """Starts the capture thread."""
        logger.info(f"Starting stream: {self.name} ({self.source})")
        self.stopped = False
        self.thread.start()
        return self

    def _connect(self):
        """Attempts to open the video source."""
        if self.cap is not None:
            self.cap.release()
            
        logger.debug(f"Connecting to {self.name}...")
        self.cap = cv2.VideoCapture(self.source)
        
        # Buffer optimization
        if isinstance(self.source, str) and "rtsp" in self.source.lower():
            # For RTSP, we want minimal latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
        self.connected = self.cap.isOpened()
        if not self.connected:
            logger.error(f"Failed to open source: {self.source}")
        else:
            logger.success(f"Connected to {self.name}")

    def _update(self):
        """Main capture loop."""
        while not self.stopped:
            if not self.connected:
                # Reconnection logic with cooldown
                if time.time() - self.last_reconnect_time > 5:
                    self._connect()
                    self.last_reconnect_time = time.time()
                else:
                    time.sleep(1)
                    continue

            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from {self.name}. Reconnecting...")
                self.connected = False
                continue

            # Maintain frame rate limit
            current_time = time.time()
            elapsed = current_time - self.start_time
            if elapsed > 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.start_time = current_time

            # Manage queue (drop old frames to keep live)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame)
                except:
                    pass
            
            self.frame_count += 1
            
            # FPS Throttling
            if self.fps_limit > 0:
                time.sleep(1.0 / self.fps_limit)

    def read(self) -> Optional[cv2.Mat]:
        """Returns the most recent frame from the queue."""
        if self.frame_queue.empty():
            return None
        return self.frame_queue.get()

    def stop(self):
        """Stops the capture thread and releases resources."""
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
        self.connected = False
        logger.info(f"Stream {self.name} stopped.")

    def is_running(self) -> bool:
        return self.connected and not self.stopped
