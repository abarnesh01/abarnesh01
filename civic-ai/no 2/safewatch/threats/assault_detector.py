import numpy as np
from typing import List, Dict, Any
from loguru import logger

class AssaultDetector:
    """Detects assault by identifying attacker/victim roles and impact trajectory."""

    def __init__(self, impact_threshold: float = 25.0):
        self.impact_threshold = impact_threshold

    def detect(self, persons: List[Dict[str, Any]], motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes high-velocity interactions and directional movement.
        """
        if len(persons) < 2:
            return {"detected": False, "confidence": 0.0}

        # Find person with highest velocity (potential attacker)
        max_velocity = 0.0
        attacker_id = -1
        
        for p in persons:
            v = p.get("velocity", 0.0)
            if v > max_velocity:
                max_velocity = v
                attacker_id = p["id"]

        confidence = 0.0
        if max_velocity > self.impact_threshold:
            confidence += 0.4
            
        # If optical flow spikes near a person
        if motion_data.get("spike_detected"):
            confidence += 0.3
            
        # Pose evidence
        for p in persons:
            if p.get("action") in ["Punching", "Kicking"]:
                confidence += 0.5
                attacker_id = p["id"]

        confidence = min(confidence, 1.0)
        return {
            "detected": confidence > 0.85,
            "confidence": confidence,
            "attacker_id": attacker_id,
            "type": "Physical Assault"
        }
