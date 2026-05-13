from typing import List, Dict, Any
import numpy as np

class AssaultDetector:
    """
    Detects targeted assault behaviors.
    Criteria: Rapid approach followed by high intensity interaction.
    """
    def __init__(self):
        pass

    def detect(self, detections: List[Dict[str, Any]], velocities: Dict[int, float], poses: Dict[int, Any]) -> List[Dict[str, Any]]:
        threats = []
        # Similar logic to fight detector but focusing on asymmetry
        # If one person has very high wrist velocity towards another
        
        for det in detections:
            tid = det['id']
            if tid in poses:
                landmarks = poses[tid]
                # Check wrist velocities (simplification: if wrist is moving very fast relative to hips)
                # For brevity, we'll use a combined metric
                v = velocities.get(tid, 0)
                if v > 400:
                    # Check if they are close to someone else
                    for other in detections:
                        if other['id'] == tid: continue
                        
                        c1 = np.array([(det['bbox'][0] + det['bbox'][2])/2, (det['bbox'][1] + det['bbox'][3])/2])
                        c2 = np.array([(other['bbox'][0] + other['bbox'][2])/2, (other['bbox'][1] + other['bbox'][3])/2])
                        dist = np.linalg.norm(c1 - c2)
                        
                        if dist < 100:
                            threats.append({
                                "type": "ASSAULT",
                                "severity": "CRITICAL",
                                "confidence": min(1.0, v / 600.0),
                                "ids": [tid, other['id']],
                                "description": f"Targeted assault behavior detected: ID {tid} on {other['id']}"
                            })
        return threats
