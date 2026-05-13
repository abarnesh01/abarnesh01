from typing import Dict, Any
from loguru import logger

class CrowdPanicDetector:
    """Detects crowd panic based on optical flow divergence and high-speed movement."""

    def __init__(self, divergence_threshold: float = 2.0, magnitude_threshold: float = 15.0):
        self.divergence_threshold = divergence_threshold
        self.magnitude_threshold = magnitude_threshold

    def detect(self, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes motion vectors for signs of mass movement in multiple directions.
        """
        avg_mag = motion_data.get("avg_magnitude", 0.0)
        divergence = motion_data.get("divergence", 0.0)

        panic_score = 0.0
        if avg_mag > self.magnitude_threshold:
            panic_score += 0.4
        
        if divergence > self.divergence_threshold:
            panic_score += 0.5

        confidence = min(panic_score, 1.0)
        
        return {
            "detected": confidence > 0.6,
            "confidence": confidence,
            "avg_magnitude": avg_mag,
            "divergence": divergence
        }
