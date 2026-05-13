import time
from typing import List, Dict, Any
from classifier.skeleton_analyzer import SkeletonAnalyzer

class UnconsciousDetector:
    """
    Detects prolonged stillness in a horizontal posture.
    """
    def __init__(self, stillness_threshold: int = 15):
        self.stillness_threshold = stillness_threshold
        # {id: start_time}
        self.horizontal_history: Dict[int, float] = {}

    def detect(self, detections: List[Dict[str, Any]], poses: Dict[int, Any], velocities: Dict[int, float]) -> List[Dict[str, Any]]:
        threats = []
        current_time = time.time()
        active_ids = set()

        for det in detections:
            tid = det['id']
            if tid not in poses: continue
            
            active_ids.add(tid)
            posture = SkeletonAnalyzer.get_posture_score(poses[tid])
            v = velocities.get(tid, 0)
            
            if posture.get('horizontal', 0) > 0.8 and v < 5:
                if tid not in self.horizontal_history:
                    self.horizontal_history[tid] = current_time
                else:
                    duration = current_time - self.horizontal_history[tid]
                    if duration > self.stillness_threshold:
                        threats.append({
                            "type": "UNCONSCIOUS",
                            "severity": "HIGH",
                            "confidence": min(1.0, duration / 60.0),
                            "ids": [tid],
                            "description": f"Person ID {tid} has been horizontal and still for {int(duration)}s"
                        })
            else:
                if tid in self.horizontal_history:
                    del self.horizontal_history[tid]

        # Cleanup lost tracks
        lost_ids = set(self.horizontal_history.keys()) - active_ids
        for lid in lost_ids:
            del self.horizontal_history[lid]

        return threats
