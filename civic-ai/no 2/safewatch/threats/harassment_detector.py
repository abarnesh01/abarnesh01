import numpy as np
from typing import List, Dict, Any
from loguru import logger

class HarassmentDetector:
    """Detects harassment using sustained proximity and circling behavior."""

    def __init__(self, proximity_threshold: float = 80, time_threshold: int = 15):
        self.proximity_threshold = proximity_threshold
        self.time_threshold = time_threshold # in sampled frames
        self.interaction_history: Dict[str, int] = {} # "id1_id2" -> count

    def detect(self, persons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detects sustained close proximity between two individuals.
        """
        if len(persons) < 2:
            return {"detected": False, "confidence": 0.0}

        detected_harassment = False
        max_confidence = 0.0
        
        # Check every pair
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                p1, p2 = persons[i], persons[j]
                
                c1 = np.array([(p1['bbox'][0] + p1['bbox'][2]) / 2, (p1['bbox'][1] + p1['bbox'][3]) / 2])
                c2 = np.array([(p2['bbox'][0] + p2['bbox'][2]) / 2, (p2['bbox'][1] + p2['bbox'][3]) / 2])
                
                dist = np.linalg.norm(c1 - c2)
                pair_key = f"{min(p1['id'], p2['id'])}_{max(p1['id'], p2['id'])}"
                
                if dist < self.proximity_threshold:
                    self.interaction_history[pair_key] = self.interaction_history.get(pair_key, 0) + 1
                else:
                    self.interaction_history[pair_key] = max(0, self.interaction_history.get(pair_key, 0) - 1)

                duration = self.interaction_history[pair_key]
                if duration > self.time_threshold:
                    detected_harassment = True
                    confidence = min(0.5 + (duration / 100), 1.0)
                    max_confidence = max(max_confidence, confidence)

        return {
            "detected": detected_harassment,
            "confidence": max_confidence,
            "evidence": "Sustained aggressive proximity" if detected_harassment else ""
        }
