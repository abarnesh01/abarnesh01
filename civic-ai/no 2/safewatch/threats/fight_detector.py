import numpy as np
from typing import List, Dict, Any
from classifier.skeleton_analyzer import SkeletonAnalyzer

class FightDetector:
    """
    Detects physical altercations between multiple persons.
    Criteria: Proximity, high limb velocity, aggressive postures.
    """
    def __init__(self, proximity_threshold: int = 150):
        self.proximity_threshold = proximity_threshold

    def detect(self, detections: List[Dict[str, Any]], poses: Dict[int, Any], velocities: Dict[int, float]) -> List[Dict[str, Any]]:
        threats = []
        if len(detections) < 2:
            return threats

        # Check proximity between all pairs
        for i in range(len(detections)):
            for j in range(i + 1, len(detections)):
                d1 = detections[i]
                d2 = detections[j]
                
                # Center coordinates
                c1 = np.array([(d1['bbox'][0] + d1['bbox'][2])/2, (d1['bbox'][1] + d1['bbox'][3])/2])
                c2 = np.array([(d2['bbox'][0] + d2['bbox'][2])/2, (d2['bbox'][1] + d2['bbox'][3])/2])
                
                dist = np.linalg.norm(c1 - c2)
                
                if dist < self.proximity_threshold:
                    # Potential interaction, check intensity
                    v1 = velocities.get(d1['id'], 0)
                    v2 = velocities.get(d2['id'], 0)
                    
                    # High velocity + Proximity = Possible fight
                    if v1 > 300 or v2 > 300:
                        # Check postures if poses available
                        p1 = SkeletonAnalyzer.get_posture_score(poses.get(d1['id'], []))
                        p2 = SkeletonAnalyzer.get_posture_score(poses.get(d2['id'], []))
                        
                        aggression_score = (p1.get('arms_raised', 0) + p2.get('arms_raised', 0)) / 2
                        
                        if aggression_score > 0.5:
                            threats.append({
                                "type": "FIGHT",
                                "severity": "HIGH",
                                "confidence": min(1.0, (v1+v2)/1000 + aggression_score),
                                "ids": [d1['id'], d2['id']],
                                "description": f"Physical altercation between ID {d1['id']} and {d2['id']}"
                            })
                            
        return threats
