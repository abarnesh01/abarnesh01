from typing import List, Dict, Any
from loguru import logger

class AccidentDetector:
    """Detects accidents using multi-person collapse and sudden motion patterns."""

    def __init__(self):
        pass

    def detect(self, 
               falls: List[Dict[str, Any]], 
               unconscious: List[Dict[str, Any]], 
               motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines multiple threat indicators to detect a larger scale accident.
        """
        fall_count = len(falls)
        unconscious_count = len(unconscious)
        spike = motion_data.get("spike_detected", False)

        confidence = 0.0
        
        # Multi-person fall is a strong accident indicator
        if fall_count >= 2:
            confidence += 0.6
        elif fall_count == 1:
            confidence += 0.2

        if unconscious_count >= 1:
            confidence += 0.3
            
        if spike:
            confidence += 0.2

        confidence = min(confidence, 1.0)
        
        return {
            "detected": confidence > 0.7,
            "confidence": confidence,
            "evidence": {
                "falls": fall_count,
                "unconscious": unconscious_count,
                "motion_spike": spike
            }
        }
