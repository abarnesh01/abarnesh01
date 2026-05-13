import cv2
import time
from typing import Optional
from loguru import logger

class FrameSampler:
    """Smart frame sampling based on motion and fixed intervals to reduce CPU load."""

    def __init__(self, motion_threshold: float = 500, skip_interval: int = 1):
        self.motion_threshold = motion_threshold
        self.skip_interval = skip_interval
        self.frame_idx = 0
        self.prev_gray: Optional[cv2.Mat] = None
        
        # Background Subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)

    def should_process(self, frame: cv2.Mat) -> bool:
        """Determines if the current frame should be processed based on motion and skip interval."""
        self.frame_idx += 1
        
        # 1. Fixed interval sampling
        if self.frame_idx % (self.skip_interval + 1) != 0:
            return False

        # 2. Motion-aware sampling
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return True

        # Calculate difference between current frame and previous frame
        frame_delta = cv2.absdiff(self.prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Calculate motion score (sum of white pixels)
        motion_score = cv2.countNonZero(thresh)
        self.prev_gray = gray

        if motion_score > self.motion_threshold:
            logger.debug(f"Motion detected: score={motion_score}")
            return True
            
        return False

    def reset(self):
        self.prev_gray = None
        self.frame_idx = 0
