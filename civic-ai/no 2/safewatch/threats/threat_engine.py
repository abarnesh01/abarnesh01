import time
from typing import List, Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass, asdict

@dataclass
class ThreatEvent:
    camera_id: str
    threat_type: str
    severity: str
    confidence: float
    timestamp: float
    description: str
    metadata: Dict[str, Any]

class ThreatEngine:
    """Core intelligence coordinator that aggregates detections into high-level events."""

    def __init__(self, camera_id: str, config: Dict[str, Any]):
        self.camera_id = camera_id
        self.config = config
        
        # Initialize detectors (using imports relative to the package structure)
        from .fight_detector import FightDetector
        from .fall_detector import FallDetector
        from .harassment_detector import HarassmentDetector
        from .assault_detector import AssaultDetector
        from .unconscious_detector import UnconsciousDetector
        from .trespass_detector import TrespassDetector
        from .crowd_panic_detector import CrowdPanicDetector
        from .accident_detector import AccidentDetector
        from .abuse_detector import AbuseDetector

        self.detectors = {
            "fight": FightDetector(),
            "fall": FallDetector(),
            "harassment": HarassmentDetector(),
            "assault": AssaultDetector(),
            "unconscious": UnconsciousDetector(),
            "trespass": TrespassDetector(),
            "crowd_panic": CrowdPanicDetector(),
            "accident": AccidentDetector(),
            "abuse": AbuseDetector()
        }
        
        self.cooldowns: Dict[str, float] = {}
        self.default_cooldown = config.get("alerts", {}).get("cooldown", 60)

    def process(self, 
                persons: List[Dict[str, Any]], 
                motion_data: Dict[str, Any], 
                trespassers: List[Dict[str, Any]]) -> List[ThreatEvent]:
        """
        Executes all detectors and aggregates results.
        """
        events = []
        now = time.time()

        # 1. Trespass Detection
        trespass_res = self.detectors["trespass"].detect(trespassers)
        if trespass_res["detected"]:
            events.append(self._create_event("TRESPASS", "MEDIUM", trespass_res["confidence"], "Restricted zone entry", trespass_res))

        # 2. Fight Detection
        fight_res = self.detectors["fight"].detect(persons, motion_data)
        if fight_res["detected"]:
            events.append(self._create_event("FIGHT", "HIGH", fight_res["confidence"], "Aggressive behavior detected", fight_res))

        # 3. Fall Detection (per person)
        falls = []
        for p in persons:
            history = p.get("pose_history", [])
            fall_res = self.detectors["fall"].detect(p, history)
            if fall_res["detected"]:
                falls.append(fall_res)
                events.append(self._create_event("FALL", "MEDIUM", fall_res["confidence"], f"Person ID {p['id']} fell", fall_res))

        # 4. Unconscious Detection
        unconscious_res = self.detectors["unconscious"].detect(persons)
        for u in unconscious_res:
            events.append(self._create_event("UNCONSCIOUS", "CRITICAL", u["confidence"], f"Person ID {u['id']} is unconscious", u))

        # 5. Crowd Panic Detection
        panic_res = self.detectors["crowd_panic"].detect(motion_data)
        if panic_res["detected"]:
            events.append(self._create_event("CROWD_PANIC", "HIGH", panic_res["confidence"], "Unusual crowd movement", panic_res))

        # 6. Accident Detection (Aggregated)
        accident_res = self.detectors["accident"].detect(falls, unconscious_res, motion_data)
        if accident_res["detected"]:
            events.append(self._create_event("ACCIDENT", "CRITICAL", accident_res["confidence"], "Major accident detected", accident_res))

        # Filter events by cooldown
        filtered_events = []
        for event in events:
            if self._is_on_cooldown(event.threat_type):
                continue
            filtered_events.append(event)
            self.cooldowns[event.threat_type] = now

        return filtered_events

    def _create_event(self, t_type: str, severity: str, conf: float, desc: str, meta: Dict) -> ThreatEvent:
        return ThreatEvent(
            camera_id=self.camera_id,
            threat_type=t_type,
            severity=severity,
            confidence=conf,
            timestamp=time.time(),
            description=desc,
            metadata=meta
        )

    def _is_on_cooldown(self, threat_type: str) -> bool:
        if threat_type not in self.cooldowns:
            return False
        return (time.time() - self.cooldowns[threat_type]) < self.default_cooldown
