import time
import numpy as np
from typing import List, Dict, Any

class HarassmentDetector:
    """
    Detects harassment behaviors like sustained proximity and following.
    """
    def __init__(self, time_threshold: int = 10, dist_threshold: int = 100):
        self.time_threshold = time_threshold
        self.dist_threshold = dist_threshold
        # { (id1, id2): start_time }
        self.proximity_history: Dict[tuple, float] = {}

    def detect(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        threats = []
        current_time = time.time()
        active_pairs = set()

        if len(detections) < 2:
            return threats

        for i in range(len(detections)):
            for j in range(i + 1, len(detections)):
                d1 = detections[i]
                d2 = detections[j]
                
                c1 = np.array([(d1['bbox'][0] + d1['bbox'][2])/2, (d1['bbox'][1] + d1['bbox'][3])/2])
                c2 = np.array([(d2['bbox'][0] + d2['bbox'][2])/2, (d2['bbox'][1] + d2['bbox'][3])/2])
                
                dist = np.linalg.norm(c1 - c2)
                
                if dist < self.dist_threshold:
                    pair = tuple(sorted((d1['id'], d2['id'])))
                    active_pairs.add(pair)
                    
                    if pair not in self.proximity_history:
                        self.proximity_history[pair] = current_time
                    else:
                        duration = current_time - self.proximity_history[pair]
                        if duration > self.time_threshold:
                            threats.append({
                                "type": "HARASSMENT",
                                "severity": "MEDIUM",
                                "confidence": min(1.0, duration / 30.0),
                                "ids": list(pair),
                                "description": f"Sustained proximity between {pair[0]} and {pair[1]}"
                            })
                            
        # Cleanup inactive pairs
        lost_pairs = set(self.proximity_history.keys()) - active_pairs
        for lp in lost_pairs:
            del self.proximity_history[lp]

        return threats
