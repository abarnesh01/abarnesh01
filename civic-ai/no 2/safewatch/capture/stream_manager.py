import threading
from typing import Dict, List, Optional
from loguru import logger
from .camera_stream import CameraStream

class StreamManager:
    """Manages multiple camera streams and monitors their health."""

    def __init__(self):
        self.streams: Dict[str, CameraStream] = {}
        self.lock = threading.Lock()

    def add_camera(self, camera_id: str, source: str, fps_limit: int = 15):
        """Adds and starts a new camera stream."""
        with self.lock:
            if camera_id in self.streams:
                logger.warning(f"Camera {camera_id} already exists. Stopping old stream.")
                self.streams[camera_id].stop()
            
            stream = CameraStream(camera_id, source, fps_limit)
            self.streams[camera_id] = stream.start()
            logger.info(f"Added camera {camera_id} to StreamManager.")

    def remove_camera(self, camera_id: str):
        """Stops and removes a camera stream."""
        with self.lock:
            if camera_id in self.streams:
                self.streams[camera_id].stop()
                del self.streams[camera_id]
                logger.info(f"Removed camera {camera_id} from StreamManager.")

    def get_stream(self, camera_id: str) -> Optional[CameraStream]:
        """Retrieves a specific camera stream."""
        return self.streams.get(camera_id)

    def get_all_streams(self) -> List[CameraStream]:
        """Returns all managed streams."""
        return list(self.streams.values())

    def get_health_report(self) -> List[dict]:
        """Generates a health status report for all cameras."""
        return [stream.get_status() for stream in self.streams.values()]

    def stop_all(self):
        """Stops all camera streams."""
        with self.lock:
            for camera_id, stream in self.streams.items():
                stream.stop()
            self.streams.clear()
            logger.info("Stopped all camera streams.")
