"""
SafeWatch — Stream Manager
Manages multiple camera streams with health monitoring and auto-restart.
"""

import threading
import time
from typing import Any, Optional

import numpy as np
from loguru import logger

from capture.camera_stream import CameraStream
from capture.frame_sampler import FrameSampler


class StreamManager:
    """Manages multiple CameraStream instances from configuration."""

    def __init__(self, camera_configs: list[dict[str, Any]]) -> None:
        self._configs = camera_configs
        self._streams: dict[str, CameraStream] = {}
        self._samplers: dict[str, FrameSampler] = {}
        self._lock = threading.Lock()
        self._health_thread: Optional[threading.Thread] = None
        self._running = False

        for cam_cfg in camera_configs:
            if cam_cfg.get("enabled", False):
                cam_id = cam_cfg["id"]
                resolution = tuple(cam_cfg.get("resolution", [640, 480]))
                stream = CameraStream(
                    source=cam_cfg["source"],
                    camera_id=cam_id,
                    resolution=resolution,
                    fps_target=cam_cfg.get("fps_target", 15),
                    buffer_size=128,
                )
                sampler = FrameSampler(
                    camera_stream=stream,
                    frame_skip=cam_cfg.get("frame_skip", 5),
                    resolution=resolution,
                )
                self._streams[cam_id] = stream
                self._samplers[cam_id] = sampler

        logger.info(f"StreamManager initialized with {len(self._streams)} cameras")

    def __repr__(self) -> str:
        cams = ", ".join(self._streams.keys())
        return f"StreamManager(cameras=[{cams}])"

    def start_all(self) -> None:
        """Start all enabled camera streams."""
        self._running = True
        for cam_id, stream in self._streams.items():
            logger.info(f"Starting stream: {cam_id}")
            stream.start()

        self._health_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True,
            name="stream-health",
        )
        self._health_thread.start()
        logger.info("All camera streams started")

    def stop_all(self) -> None:
        """Stop all camera streams."""
        self._running = False
        for cam_id, stream in self._streams.items():
            logger.info(f"Stopping stream: {cam_id}")
            stream.stop()
        logger.info("All camera streams stopped")

    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get the latest frame from a specific camera."""
        with self._lock:
            stream = self._streams.get(camera_id)
        if stream is None:
            return None
        return stream.read()

    def get_frame_data(self, camera_id: str) -> Optional[dict[str, Any]]:
        """Get a full frame_data dict from a specific camera's sampler."""
        with self._lock:
            sampler = self._samplers.get(camera_id)
        if sampler is None:
            return None
        return sampler.get_single_frame()

    def get_sampler(self, camera_id: str) -> Optional[FrameSampler]:
        """Get the FrameSampler for a camera."""
        with self._lock:
            return self._samplers.get(camera_id)

    def get_stream(self, camera_id: str) -> Optional[CameraStream]:
        """Get the CameraStream for a camera."""
        with self._lock:
            return self._streams.get(camera_id)

    def get_all_camera_ids(self) -> list[str]:
        """Get list of all managed camera IDs."""
        with self._lock:
            return list(self._streams.keys())

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get health status of all cameras."""
        status = {}
        with self._lock:
            for cam_id, stream in self._streams.items():
                status[cam_id] = {
                    "running": stream.is_running(),
                    "connected": stream.is_connected(),
                    "fps": stream.get_fps(),
                    "source": stream.source,
                }
        return status

    def _health_monitor_loop(self) -> None:
        """Periodically log health and auto-restart failed streams."""
        while self._running:
            time.sleep(60)
            if not self._running:
                break

            status = self.get_status()
            for cam_id, info in status.items():
                if info["running"] and not info["connected"]:
                    logger.warning(
                        f"[{cam_id}] Camera disconnected (FPS={info['fps']}), "
                        f"auto-reconnect active"
                    )
                elif info["running"] and info["connected"]:
                    logger.debug(f"[{cam_id}] Healthy — FPS={info['fps']}")
                elif not info["running"]:
                    logger.warning(f"[{cam_id}] Stream thread stopped, restarting...")
                    with self._lock:
                        stream = self._streams.get(cam_id)
                    if stream:
                        stream.start()

    def is_any_running(self) -> bool:
        """Check if any camera is running."""
        return any(s.is_running() for s in self._streams.values())
