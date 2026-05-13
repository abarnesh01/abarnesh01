import cv2
import time
from loguru import logger

class FrameSampler:
    """
    Optimizes processing load by intelligently sampling frames.
    Implements motion-aware skipping and fixed interval sampling.
    """
    def __init__(self, sampling_rate: int = 2, motion_threshold: float = 0.01):
        self.sampling_rate = sampling_rate  # Process every Nth frame
        self.motion_threshold = motion_threshold
        self.frame_counter = 0
        self.prev_frame_gray = None
        self.last_process_time = 0

    def should_process(self, frame) -> bool:
        """
        Determines if the current frame should undergo heavy AI processing.
        """
        self.frame_counter += 1
        
        # 1. Fixed interval sampling
        if self.frame_counter % self.sampling_rate != 0:
            return False

        # 2. Motion-aware sampling (Optional optimization)
        # If no motion is detected, we can skip expensive person detection
        if self.motion_threshold > 0:
            has_motion = self._detect_motion(frame)
            if not has_motion:
                return False
        
        return True

    def _detect_motion(self, frame) -> bool:
        """
        Simple motion detection using frame differencing.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame_gray is None:
            self.prev_frame_gray = gray
            return True

        frame_delta = cv2.absdiff(self.prev_frame_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Calculate motion percentage
        motion_score = (cv2.countNonZero(thresh) / (frame.shape[0] * frame.shape[1]))
        
        self.prev_frame_gray = gray
        
        return motion_score > self.motion_threshold

    def reset(self):
        self.frame_counter = 0
        self.prev_frame_gray = None
