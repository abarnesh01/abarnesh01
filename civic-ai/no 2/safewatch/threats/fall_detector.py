from typing import List, Dict, Any
from loguru import logger

class FallDetector:
    """Detects human falls using hip-drop analysis and posture transitions."""

    def __init__(self, drop_threshold: float = 0.15, orientation_threshold: float = 60.0):
        self.drop_threshold = drop_threshold
        self.orientation_threshold = orientation_threshold

    def detect(self, person: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes current pose and history for fall patterns.
        """
        features = person.get("pose_features", {})
        if not features or not history:
            return {"detected": False, "confidence": 0.0}

        # 1. Check current posture
        is_horizontal = features.get("is_horizontal", False)
        torso_angle = features.get("torso_angle", 0.0)

        # 2. Check history for rapid drop
        start_hip = history[0].get("hip_height", features.get("hip_height", 0))
        end_hip = features.get("hip_height", 0)
        hip_drop = end_hip - start_hip # Y increases downwards

        confidence = 0.0
        if is_horizontal:
            confidence += 0.4
            if hip_drop > self.drop_threshold:
                confidence += 0.5
            
        # 3. Action classifier check
        if person.get("action") == "Falling":
            confidence += 0.6

        confidence = min(confidence, 1.0)
        
        return {
            "detected": confidence > 0.75,
            "confidence": confidence,
            "hip_drop": float(hip_drop),
            "torso_angle": float(torso_angle)
        }
