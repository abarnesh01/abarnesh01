import threading
import time
from loguru import logger
from typing import Dict, List, Optional
from capture.camera_stream import CameraStream
from database.incident_logger import IncidentLogger

class StreamManager:
    """
    Orchestrates multiple CameraStream instances.
    Handles startup, health monitoring, and graceful shutdown.
    """
    def __init__(self, camera_configs: List[Dict]):
        self.streams: Dict[int, CameraStream] = {}
        self.configs = camera_configs
        self.running = False
        self.monitor_thread = threading.Thread(target=self._monitor_health, name="StreamMonitor", daemon=True)

    def start_all(self):
        """Initializes and starts all configured camera streams."""
        logger.info(f"Initializing {len(self.configs)} camera streams...")
        self.running = True
        
        for cfg in self.configs:
            if not cfg.get('enabled', True):
                continue
                
            stream = CameraStream(
                camera_id=cfg['id'],
                name=cfg['name'],
                source=cfg['source'],
                fps_limit=cfg.get('fps_limit', 30)
            )
            self.streams[cfg['id']] = stream
            stream.start()
            
        self.monitor_thread.start()

    def stop_all(self):
        """Stops all running streams gracefully."""
        logger.info("Stopping all camera streams...")
        self.running = False
        for stream in self.streams.values():
            stream.stop()
        
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logger.success("All streams shut down.")

    def _monitor_health(self):
        """Background thread to monitor and log camera health status."""
        while self.running:
            for cam_id, stream in self.streams.items():
                status = "CONNECTED" if stream.connected else "DISCONNECTED"
                IncidentLogger.update_camera_health(
                    camera_id=cam_id,
                    camera_name=stream.name,
                    status=status,
                    error_msg=None if stream.connected else "Stream connection lost"
                )
            time.sleep(10)  # Check every 10 seconds

    def get_stream(self, camera_id: int) -> Optional[CameraStream]:
        """Returns the CameraStream instance for a given ID."""
        return self.streams.get(camera_id)

    def get_active_streams(self) -> List[CameraStream]:
        """Returns a list of all currently active streams."""
        return [s for s in self.streams.values() if s.is_running()]
