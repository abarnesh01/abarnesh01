"""
SafeWatch — Frame Sampler
Smart frame sampling with motion-based adaptive skip and background subtraction.
"""

import time
from typing import Any, Generator, Optional

import cv2
import numpy as np
from loguru import logger

from capture.camera_stream import CameraStream


class FrameSampler:
    """Samples frames from a CameraStream with smart skip and motion detection."""

    def __init__(
        self,
        camera_stream: CameraStream,
        frame_skip: int = 5,
        resolution: tuple[int, int] = (640, 480),
        motion_threshold: float = 5000.0,
    ) -> None:
        self._stream = camera_stream
        self._frame_skip = frame_skip
        self._resolution = resolution
        self._motion_threshold = motion_threshold
        self._frame_number = 0
        self._bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=False,
        )
        self._last_motion_score = 0.0
        logger.info(
            f"FrameSampler created for {camera_stream.camera_id}, "
            f"skip={frame_skip}, motion_threshold={motion_threshold}"
        )

    def __repr__(self) -> str:
        return (
            f"FrameSampler(camera={self._stream.camera_id}, "
            f"skip={self._frame_skip}, frame={self._frame_number})"
        )

    def _detect_motion(self, frame: np.ndarray) -> tuple[bool, float]:
        """Detect motion using background subtraction."""
        small = cv2.resize(frame, (320, 240))
        fg_mask = self._bg_subtractor.apply(small)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        motion_score = float(np.sum(thresh) / 255.0)
        self._last_motion_score = motion_score
        has_motion = motion_score > self._motion_threshold
        return has_motion, motion_score

    def get_frame(self) -> Generator[dict[str, Any], None, None]:
        """Generator that yields frame data dicts with smart sampling."""
        while self._stream.is_running():
            frame = self._stream.read()
            if frame is None:
                time.sleep(0.01)
                continue

            self._frame_number += 1
            has_motion, motion_score = self._detect_motion(frame)

            should_process = (self._frame_number % self._frame_skip == 0) or has_motion

            if should_process:
                frame = cv2.resize(frame, self._resolution)
                frame_data: dict[str, Any] = {
                    "frame": frame,
                    "camera_id": self._stream.camera_id,
                    "timestamp": time.time(),
                    "frame_number": self._frame_number,
                    "has_motion": has_motion,
                    "motion_score": motion_score,
                }
                yield frame_data
            else:
                time.sleep(0.001)

    def get_single_frame(self) -> Optional[dict[str, Any]]:
        """Get a single frame (non-generator), useful for dashboard snapshots."""
        frame = self._stream.read()
        if frame is None:
            return None

        self._frame_number += 1
        has_motion, motion_score = self._detect_motion(frame)
        frame = cv2.resize(frame, self._resolution)

        return {
            "frame": frame,
            "camera_id": self._stream.camera_id,
            "timestamp": time.time(),
            "frame_number": self._frame_number,
            "has_motion": has_motion,
            "motion_score": motion_score,
        }

    def update_skip_rate(self, n: int) -> None:
        """Dynamically adjust the frame skip rate."""
        self._frame_skip = max(1, n)
        logger.info(f"[{self._stream.camera_id}] Frame skip updated to {self._frame_skip}")

    @property
    def frame_number(self) -> int:
        return self._frame_number

    @property
    def last_motion_score(self) -> float:
        return self._last_motion_score
