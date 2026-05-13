from typing import List, Dict, Any
from loguru import logger

class UnconsciousDetector:
    """Detects unconscious persons based on prolonged horizontal stillness."""

    def __init__(self, stillness_frames: int = 100):
        self.stillness_frames = stillness_frames
        self.stillness_counters: Dict[int, int] = {} # id -> frames

    def detect(self, persons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects individuals lying down with near-zero movement for a long time.
        """
        unconscious_persons = []
        active_ids = []

        for p in persons:
            active_ids.append(p["id"])
            features = p.get("pose_features", {})
            velocity = p.get("velocity", 0.0)
            
            # Condition: Horizontal posture + low velocity
            if features.get("is_horizontal") and velocity < 2.0:
                self.stillness_counters[p["id"]] = self.stillness_counters.get(p["id"], 0) + 1
            else:
                self.stillness_counters[p["id"]] = 0

            if self.stillness_counters[p["id"]] > self.stillness_frames:
                unconscious_persons.append({
                    "id": p["id"],
                    "confidence": 0.9,
                    "duration": self.stillness_counters[p["id"]]
                })

        # Cleanup
        self.stillness_counters = {k: v for k, v in self.stillness_counters.items() if k in active_ids}
        
        return unconscious_persons
