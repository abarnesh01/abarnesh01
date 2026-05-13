import numpy as np
from typing import List, Dict, Any
from loguru import logger

class FightDetector:
    """Detects fighting behavior using multi-person aggression scoring."""

    def __init__(self, proximity_threshold: float = 100, velocity_threshold: float = 20.0):
        self.proximity_threshold = proximity_threshold
        self.velocity_threshold = velocity_threshold

    def detect(self, persons: List[Dict[str, Any]], motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes relationships between persons and motion spikes to detect fights.
        """
        if len(persons) < 2:
            return {"detected": False, "confidence": 0.0}

        fight_score = 0.0
        evidence = []

        # 1. Proximity Check
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                p1 = persons[i]
                p2 = persons[j]
                
                # Centers of bounding boxes
                c1 = np.array([(p1['bbox'][0] + p1['bbox'][2]) / 2, (p1['bbox'][1] + p1['bbox'][3]) / 2])
                c2 = np.array([(p2['bbox'][0] + p2['bbox'][2]) / 2, (p2['bbox'][1] + p2['bbox'][3]) / 2])
                
                dist = np.linalg.norm(c1 - c2)
                
                if dist < self.proximity_threshold:
                    fight_score += 0.3
                    evidence.append(f"Aggressive proximity between {p1['id']} and {p2['id']}")

        # 2. Motion Spike Check (from Optical Flow)
        if motion_data.get("spike_detected", False):
            fight_score += 0.4
            evidence.append("High-velocity motion spike detected")

        # 3. Pose-based Aggression (if available)
        for p in persons:
            features = p.get("pose_features", {})
            if features.get("l_arm_raised") or features.get("r_arm_raised"):
                fight_score += 0.15
                evidence.append(f"Raised arm detected for ID {p['id']}")
            
            # Action classification
            if p.get("action") in ["Fighting", "Punching", "Kicking"]:
                fight_score += 0.5
                evidence.append(f"Action '{p['action']}' classified for ID {p['id']}")

        confidence = min(fight_score, 1.0)
        return {
            "detected": confidence > 0.7,
            "confidence": confidence,
            "evidence": list(set(evidence))
        }
