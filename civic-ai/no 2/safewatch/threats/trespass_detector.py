from typing import List, Dict, Any

class TrespassDetector:
    """
    Detects persons entering prohibited zones.
    """
    def __init__(self):
        pass

    def detect(self, detections: List[Dict[str, Any]], zone_activity: Dict[int, List[str]]) -> List[Dict[str, Any]]:
        threats = []
        
        for det in detections:
            tid = det['id']
            active_zones = zone_activity.get(tid, [])
            
            for zone in active_zones:
                if "RESTRICTED" in zone.upper() or "TRESPASS" in zone.upper():
                    threats.append({
                        "type": "TRESPASSING",
                        "severity": "MEDIUM",
                        "confidence": det['confidence'],
                        "ids": [tid],
                        "description": f"Person ID {tid} entered restricted zone: {zone}"
                    })
                    
        return threats
