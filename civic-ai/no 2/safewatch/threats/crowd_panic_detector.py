from typing import List, Dict, Any

class CrowdPanicDetector:
    """
    Detects crowd panic based on optical flow divergence and high multi-person velocity.
    """
    def __init__(self, panic_threshold: float = 0.6):
        self.panic_threshold = panic_threshold

    def detect(self, detections: List[Dict[str, Any]], velocities: Dict[int, float], panic_score: float) -> List[Dict[str, Any]]:
        threats = []
        
        # Combine optical flow score with person count and average velocity
        if len(detections) >= 3:
            avg_v = sum(velocities.values()) / len(velocities) if velocities else 0
            
            # High panic score from optical flow OR very high average velocity in a group
            if panic_score > self.panic_threshold or avg_v > 400:
                threats.append({
                    "type": "CROWD_PANIC",
                    "severity": "CRITICAL",
                    "confidence": max(panic_score, min(1.0, avg_v / 600.0)),
                    "ids": [d['id'] for d in detections],
                    "description": f"Crowd panic detected! Flow score: {panic_score:.2f}, Avg Velocity: {avg_v:.2f}"
                })
                
        return threats
