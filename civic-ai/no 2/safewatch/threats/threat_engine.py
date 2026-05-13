import cv2
import time
from loguru import logger
from typing import List, Dict, Any, Optional
from threats.fight_detector import FightDetector
from threats.fall_detector import FallDetector
from threats.harassment_detector import HarassmentDetector
from threats.assault_detector import AssaultDetector
from threats.unconscious_detector import UnconsciousDetector
from threats.trespass_detector import TrespassDetector
from threats.crowd_panic_detector import CrowdPanicDetector
from threats.accident_detector import AccidentDetector
from threats.abuse_detector import AbuseDetector

class ThreatEngine:
    """
    Central intelligence coordinator for all threat detectors.
    Aggregates findings, manages alert cooldowns, and annotates frames.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
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
        
        # Cooldown management { (camera_id, threat_type): last_alert_time }
        self.cooldowns: Dict[tuple, float] = {}
        self.cooldown_period = config.get('threats', {}).get('cooldown_seconds', 30)

    def analyze(
        self, 
        camera_id: int,
        detections: List[Dict[str, Any]], 
        poses: Dict[int, Any], 
        velocities: Dict[int, float],
        zone_activity: Dict[int, List[str]],
        panic_score: float
    ) -> List[Dict[str, Any]]:
        """
        Executes all enabled detectors and aggregates results.
        """
        all_threats = []
        
        # 1. Independent detectors
        all_threats.extend(self.detectors['fight'].detect(detections, poses, velocities))
        all_threats.extend(self.detectors['fall'].detect(detections, poses, velocities))
        all_threats.extend(self.detectors['harassment'].detect(detections))
        all_threats.extend(self.detectors['assault'].detect(detections, velocities, poses))
        all_threats.extend(self.detectors['unconscious'].detect(detections, poses, velocities))
        all_threats.extend(self.detectors['trespass'].detect(detections, zone_activity))
        all_threats.extend(self.detectors['crowd_panic'].detect(detections, velocities, panic_score))
        
        # 2. Derivative/Correlative detectors
        all_threats.extend(self.detectors['accident'].detect(all_threats))
        all_threats.extend(self.detectors['abuse'].detect(all_threats))
        
        # 3. Filter and Apply Cooldown
        filtered_threats = []
        current_time = time.time()
        
        for threat in all_threats:
            key = (camera_id, threat['type'])
            if current_time - self.cooldowns.get(key, 0) > self.cooldown_period:
                filtered_threats.append(threat)
                self.cooldowns[key] = current_time
                
        return filtered_threats

    def draw_overlays(self, frame: cv2.Mat, threats: List[Dict[str, Any]]):
        """Renders threat banners and severity indicators on the frame."""
        for threat in threats:
            color = self._get_severity_color(threat['severity'])
            
            # Header banner
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), color, -1)
            text = f"ALERT: {threat['type']} | SEVERITY: {threat['severity']} | CONF: {threat['confidence']:.2f}"
            cv2.putText(frame, text, (20, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Side border
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 10)
            
        return frame

    def _get_severity_color(self, severity: str) -> tuple:
        colors = {
            "SAFE": (0, 255, 0),       # Green
            "LOW": (0, 255, 255),     # Yellow
            "MEDIUM": (0, 165, 255),  # Orange
            "HIGH": (0, 0, 255),      # Red
            "CRITICAL": (128, 0, 128) # Purple
        }
        return colors.get(severity, (255, 255, 255))
