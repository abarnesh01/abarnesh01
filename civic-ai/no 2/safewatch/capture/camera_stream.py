"""
SafeWatch — Camera Stream
Threaded camera capture with buffering, reconnection, and FPS tracking.
"""

import threading
import time
from collections import deque
from typing import Optional, Union

import cv2
import numpy as np
from loguru import logger


class CameraStream:
    """Threaded camera stream with auto-reconnection and frame buffering."""

    def __init__(
        self,
        source: Union[int, str],
        camera_id: str = "CAM-00",
        resolution: tuple[int, int] = (640, 480),
        fps_target: int = 15,
        buffer_size: int = 128,
    ) -> None:
        self._source = source
        self._camera_id = camera_id
        self._resolution = resolution
        self._fps_target = fps_target
        self._buffer: deque[np.ndarray] = deque(maxlen=buffer_size)
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._connected = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._fps = 0.0
        self._frame_count = 0
        self._fps_timer = time.time()
        self._reconnect_delay = 5.0
        logger.info(f"CameraStream created: id={camera_id}, source={source}, res={resolution}")

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"CameraStream(id='{self._camera_id}', source={self._source}, status={status})"

    def _open_capture(self) -> bool:
        """Open the video capture device."""
        try:
            if isinstance(self._source, int):
                self._cap = cv2.VideoCapture(self._source)
            else:
                self._cap = cv2.VideoCapture(self._source, cv2.CAP_FFMPEG)

            if self._cap is None or not self._cap.isOpened():
                logger.warning(f"[{self._camera_id}] Failed to open source: {self._source}")
                self._connected = False
                return False

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

            if isinstance(self._source, str) and self._source.startswith("rtsp"):
                self._cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                self._cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)

            self._connected = True
            logger.info(f"[{self._camera_id}] Camera opened successfully: {self._source}")
            return True
        except Exception as e:
            logger.error(f"[{self._camera_id}] Error opening camera: {e}")
            self._connected = False
            return False

    def _capture_loop(self) -> None:
        """Main capture loop running in a separate thread."""
        frame_interval = 1.0 / max(self._fps_target, 1)

        while self._running:
            if not self._connected or self._cap is None or not self._cap.isOpened():
                logger.warning(f"[{self._camera_id}] Connection lost, reconnecting in {self._reconnect_delay}s...")
                self._connected = False
                if self._cap is not None:
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                time.sleep(self._reconnect_delay)
                self._open_capture()
                continue

            try:
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    logger.warning(f"[{self._camera_id}] Failed to read frame")
                    self._connected = False
                    continue

                frame = cv2.resize(frame, self._resolution)

                with self._lock:
                    self._buffer.append(frame)
                    self._frame_count += 1

                elapsed = time.time() - self._fps_timer
                if elapsed >= 1.0:
                    self._fps = self._frame_count / elapsed
                    self._frame_count = 0
                    self._fps_timer = time.time()

                sleep_time = max(0.001, frame_interval - 0.005)
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"[{self._camera_id}] Capture error: {e}")
                self._connected = False
                time.sleep(0.5)

    def start(self) -> bool:
        """Start the camera stream thread."""
        if self._running:
            logger.warning(f"[{self._camera_id}] Stream already running")
            return True

        if not self._open_capture():
            logger.error(f"[{self._camera_id}] Could not start stream — camera unavailable")

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True, name=f"cam-{self._camera_id}")
        self._thread.start()
        logger.info(f"[{self._camera_id}] Stream started")
        return True

    def stop(self) -> None:
        """Stop the camera stream thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

        self._connected = False
        with self._lock:
            self._buffer.clear()
        logger.info(f"[{self._camera_id}] Stream stopped")

    def read(self) -> Optional[np.ndarray]:
        """Read the latest frame from the buffer."""
        with self._lock:
            if len(self._buffer) > 0:
                return self._buffer[-1].copy()
        return None

    def read_batch(self, n: int = 5) -> list[np.ndarray]:
        """Read the last N frames from the buffer."""
        with self._lock:
            frames = list(self._buffer)
        return [f.copy() for f in frames[-n:]]

    def get_fps(self) -> float:
        """Get the current frames per second."""
        return round(self._fps, 1)

    def is_running(self) -> bool:
        """Check if the capture thread is running."""
        return self._running

    def is_connected(self) -> bool:
        """Check if the camera is connected and producing frames."""
        return self._connected

    def get_frame_count(self) -> int:
        """Get total frames captured in the current FPS window."""
        return self._frame_count

    @property
    def camera_id(self) -> str:
        return self._camera_id

    @property
    def source(self) -> Union[int, str]:
        return self._source
