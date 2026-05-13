from typing import List, Dict, Any
from loguru import logger

class AbuseDetector:
    """Detects abuse/domestic violence through repeated strikes and posture power dynamics."""

    def __init__(self):
        self.strike_history: Dict[str, int] = {} # pair_key -> strike_count

    def detect(self, persons: List[Dict[str, Any]], fight_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Long-term analysis of aggressive interactions between the same individuals.
        """
        if not fight_event.get("detected"):
            return {"detected": False, "confidence": 0.0}

        confidence = fight_event.get("confidence", 0.0)
        
        # Check for dominant/submissive posture (one standing, one cowering/lying)
        standing_count = 0
        horizontal_count = 0
        for p in persons:
            if p.get("pose_features", {}).get("is_horizontal"):
                horizontal_count += 1
            else:
                standing_count += 1

        if standing_count >= 1 and horizontal_count >= 1:
            confidence += 0.2
            
        # Repeated aggression
        if confidence > 0.8:
            return {
                "detected": True,
                "confidence": min(confidence, 1.0),
                "type": "Abuse/Harassment Escalation"
            }

        return {"detected": False, "confidence": 0.0}
