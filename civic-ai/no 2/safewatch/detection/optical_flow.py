import cv2
import numpy as np
from loguru import logger

class OpticalFlowAnalyzer:
    """
    Analyzes global and local motion patterns using Dense Optical Flow (Farneback).
    Useful for detecting crowd panic, sudden high-velocity movements, and directional flow.
    """
    def __init__(self, scale: float = 0.5):
        self.prev_gray = None
        self.scale = scale # Resize frame for faster processing

    def compute_flow(self, frame: np.ndarray):
        """
        Computes optical flow between current and previous frame.
        Returns (magnitude, angle) of the flow field.
        """
        # Resize for speed
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray is None:
            self.prev_gray = gray
            return None, None

        # Calculate Farneback optical flow
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None, 
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        self.prev_gray = gray
        return mag, ang

    def analyze_panic(self, mag: np.ndarray) -> float:
        """
        Calculates a panic score based on sudden increase in motion magnitude.
        """
        if mag is None: return 0.0
        
        # Mean magnitude of all motion
        avg_motion = np.mean(mag)
        # Peak motion (top 5% percentile)
        peak_motion = np.percentile(mag, 95)
        
        # Score is a combination of average and peak intensity
        # Normalize to 0-1 range (heuristic)
        score = min(1.0, (avg_motion * 0.3 + peak_motion * 0.7) / 20.0)
        return float(score)

    def draw_flow(self, frame: np.ndarray, mag: np.ndarray, ang: np.ndarray):
        """Visualizes flow direction and magnitude using HSV."""
        if mag is None: return frame
        
        h, w = frame.shape[:2]
        hsv = np.zeros((mag.shape[0], mag.shape[1], 3), dtype=np.uint8)
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 1] = 255
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        
        bgr_flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr_flow = cv2.resize(bgr_flow, (w, h))
        
        # Overlay with original frame
        combined = cv2.addWeighted(frame, 0.7, bgr_flow, 0.3, 0)
        return combined
