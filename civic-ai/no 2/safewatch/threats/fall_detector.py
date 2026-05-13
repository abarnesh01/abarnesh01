from typing import List, Dict, Any
from classifier.skeleton_analyzer import SkeletonAnalyzer

class FallDetector:
    """
    Detects person falls using skeletal orientation and impact velocity.
    """
    def __init__(self, horizontal_threshold: float = 0.7):
        self.horizontal_threshold = horizontal_threshold

    def detect(self, detections: List[Dict[str, Any]], poses: Dict[int, Any], velocities: Dict[int, float]) -> List[Dict[str, Any]]:
        threats = []
        
        for det in detections:
            track_id = det['id']
            if track_id not in poses:
                continue
                
            posture = SkeletonAnalyzer.get_posture_score(poses[track_id])
            v = velocities.get(track_id, 0)
            
            # Criteria: High horizontal score + high downward velocity OR sudden stop
            if posture.get('horizontal', 0) > self.horizontal_threshold:
                # If they are horizontal and were moving fast, it's likely a fall
                if v > 150:
                    threats.append({
                        "type": "FALL",
                        "severity": "MEDIUM",
                        "confidence": posture['horizontal'],
                        "ids": [track_id],
                        "description": f"Person fall detected for ID {track_id}"
                    })
                    
        return threats
