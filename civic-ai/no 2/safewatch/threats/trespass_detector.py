from typing import List, Dict, Any
from loguru import logger

class TrespassDetector:
    """Detects individuals in restricted zones."""

    def __init__(self):
        pass

    def detect(self, trespassers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Wraps zone manager findings into a threat event.
        """
        if not trespassers:
            return {"detected": False, "confidence": 0.0}

        return {
            "detected": True,
            "confidence": 1.0,
            "count": len(trespassers),
            "zones": list(set([t["zone"] for t in trespassers])),
            "ids": [t["id"] for t in trespassers]
        }
