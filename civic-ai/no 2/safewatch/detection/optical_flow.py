import cv2
import numpy as np
from loguru import logger
from typing import Tuple, Optional

class OpticalFlowAnalyzer:
    """Real-time motion intelligence using Lucas-Kanade optical flow and divergence analysis."""

    def __init__(self, max_corners: int = 100, min_distance: int = 7, block_size: int = 7):
        # Parameters for Shi-Tomasi corner detection
        self.feature_params = dict(
            maxCorners=max_corners,
            qualityLevel=0.3,
            minDistance=min_distance,
            blockSize=block_size
        )

        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

        self.prev_gray: Optional[cv2.Mat] = None
        self.prev_points: Optional[np.ndarray] = None
        logger.info("Optical Flow Analyzer initialized.")

    def analyze(self, frame: cv2.Mat) -> dict:
        """
        Calculates motion vectors and detects sudden movement spikes or divergence.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        motion_data = {
            "avg_magnitude": 0.0,
            "max_magnitude": 0.0,
            "spike_detected": False,
            "divergence": 0.0
        }

        if self.prev_gray is None:
            self.prev_gray = gray
            self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return motion_data

        if self.prev_points is not None:
            # Calculate optical flow
            next_points, status, error = cv2.calcOpticalFlowPyrLK(
                self.prev_gray, gray, self.prev_points, None, **self.lk_params
            )

            if next_points is not None:
                # Select good points
                good_new = next_points[status == 1]
                good_old = self.prev_points[status == 1]

                if len(good_new) > 0:
                    # Calculate magnitude of vectors
                    vectors = good_new - good_old
                    magnitudes = np.sqrt(np.sum(vectors**2, axis=1))
                    
                    motion_data["avg_magnitude"] = float(np.mean(magnitudes))
                    motion_data["max_magnitude"] = float(np.max(magnitudes))
                    
                    # Spike detection (e.g., sudden dash or hit)
                    if motion_data["max_magnitude"] > 25:
                        motion_data["spike_detected"] = True

                    # Divergence calculation (crowd panic indicator)
                    # Simplified: Variance in vector directions
                    angles = np.arctan2(vectors[:, 1], vectors[:, 0])
                    motion_data["divergence"] = float(np.var(angles))

                self.prev_points = good_new.reshape(-1, 1, 2)
            else:
                self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
        else:
            self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)

        self.prev_gray = gray
        return motion_data

    def draw_flow(self, frame: cv2.Mat, motion_data: dict):
        """Visualizes motion vectors (simplified indicator)."""
        if motion_data["avg_magnitude"] > 0:
            color = (0, 0, 255) if motion_data["spike_detected"] else (0, 255, 255)
            cv2.putText(frame, f"Motion: {motion_data['avg_magnitude']:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame
