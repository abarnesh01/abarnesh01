"""
SafeWatch — Threat Engine
Central coordinator for all threat detectors with parallel execution and cooldown.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger

from classifier.velocity_tracker import VelocityTracker
from detection.optical_flow import FlowResult
from detection.person_detector import Person
from detection.pose_estimator import PoseResult
from detection.zone_manager import ZoneManager
from threats.abuse_detector import AbuseDetector
from threats.accident_detector import AccidentDetector
from threats.assault_detector import AssaultDetector
from threats.crowd_panic_detector import CrowdPanicDetector
from threats.fall_detector import FallDetector
from threats.fight_detector import FightDetector
from threats.harassment_detector import HarassmentDetector
from threats.trespass_detector import TrespassDetector
from threats.unconscious_detector import UnconsciousDetector


@dataclass
class ThreatEvent:
    """A single detected threat event."""
    threat_type: str
    confidence: float
    persons_involved: int
    person_ids: list[int]
    location_bbox: tuple[int, int, int, int]
    description: str
    severity: str
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (
            f"ThreatEvent(type='{self.threat_type}', conf={self.confidence:.2f}, "
            f"severity={self.severity})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "threat_type": self.threat_type,
            "confidence": self.confidence,
            "persons_involved": self.persons_involved,
            "person_ids": self.person_ids,
            "location_bbox": self.location_bbox,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }


@dataclass
class ThreatReport:
    """Aggregated threat report for a single frame."""
    camera_id: str
    timestamp: float
    threats_detected: list[ThreatEvent]
    annotated_frame: Optional[np.ndarray]
    overall_risk_level: str

    def __repr__(self) -> str:
        return (
            f"ThreatReport(camera={self.camera_id}, "
            f"threats={len(self.threats_detected)}, "
            f"risk={self.overall_risk_level})"
        )


class ThreatEngine:
    """Central coordinator that runs all threat detectors and aggregates results."""

    SEVERITY_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    SEVERITY_COLORS = {
        "SAFE": (0, 255, 0),
        "LOW": (0, 255, 255),
        "MEDIUM": (0, 165, 255),
        "HIGH": (0, 0, 255),
        "CRITICAL": (128, 0, 128),
    }

    def __init__(self, config: dict[str, Any], zone_manager: ZoneManager) -> None:
        threats_cfg = config.get("threats", {})
        self._zone_manager = zone_manager
        self._lock = threading.Lock()
        self._cooldowns: dict[tuple[str, str], float] = {}
        self._cooldown_seconds = config.get("telegram", {}).get("alert_cooldown_seconds", 30)

        # Initialize all detectors
        self._fight_detector = FightDetector(threats_cfg.get("fight", {}))
        self._fall_detector = FallDetector(threats_cfg.get("fall", {}))
        self._harassment_detector = HarassmentDetector(threats_cfg.get("harassment", {}))
        self._assault_detector = AssaultDetector(threats_cfg.get("assault", {}))
        self._unconscious_detector = UnconsciousDetector(threats_cfg.get("unconscious", {}))
        self._trespass_detector = TrespassDetector(threats_cfg.get("trespass", {}))
        self._crowd_panic_detector = CrowdPanicDetector(threats_cfg.get("crowd_panic", {}))
        self._accident_detector = AccidentDetector(threats_cfg.get("accident", {}))
        self._abuse_detector = AbuseDetector(threats_cfg.get("abuse", {}))

        self._enabled: dict[str, bool] = {
            "fight": threats_cfg.get("fight", {}).get("enabled", True),
            "fall": threats_cfg.get("fall", {}).get("enabled", True),
            "harassment": threats_cfg.get("harassment", {}).get("enabled", True),
            "assault": threats_cfg.get("assault", {}).get("enabled", True),
            "unconscious": threats_cfg.get("unconscious", {}).get("enabled", True),
            "trespass": threats_cfg.get("trespass", {}).get("enabled", True),
            "crowd_panic": threats_cfg.get("crowd_panic", {}).get("enabled", True),
            "accident": threats_cfg.get("accident", {}).get("enabled", True),
            "abuse": threats_cfg.get("abuse", {}).get("enabled", True),
        }

        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="threat")
        logger.info(f"ThreatEngine initialized with {sum(self._enabled.values())} enabled detectors")

    def __repr__(self) -> str:
        enabled_count = sum(self._enabled.values())
        return f"ThreatEngine(detectors={enabled_count})"

    def analyze(self, frame_data: dict[str, Any]) -> ThreatReport:
        """Run all enabled threat detectors and aggregate results."""
        frame = frame_data.get("frame")
        camera_id = frame_data.get("camera_id", "UNKNOWN")
        timestamp = frame_data.get("timestamp", time.time())
        persons: list[Person] = frame_data.get("persons", [])
        poses: list[PoseResult] = frame_data.get("poses", [])
        flow_result: Optional[FlowResult] = frame_data.get("flow_result")
        velocity_tracker: VelocityTracker = frame_data.get("velocity_tracker")
        config = frame_data.get("config", {}).get("threats", {})

        all_threats: list[dict[str, Any]] = []
        futures = {}

        # Submit detection tasks in parallel
        if self._enabled.get("fight") and len(poses) >= 2:
            futures["fight"] = self._executor.submit(
                self._fight_detector.detect, persons, poses, velocity_tracker, config
            )

        if self._enabled.get("fall"):
            futures["fall"] = self._executor.submit(
                self._fall_detector.detect, persons, poses, velocity_tracker, config
            )

        if self._enabled.get("harassment") and len(poses) >= 2:
            futures["harassment"] = self._executor.submit(
                self._harassment_detector.detect, persons, poses, velocity_tracker, config
            )

        if self._enabled.get("assault") and len(poses) >= 2:
            futures["assault"] = self._executor.submit(
                self._assault_detector.detect, persons, poses, velocity_tracker, config
            )

        if self._enabled.get("unconscious"):
            futures["unconscious"] = self._executor.submit(
                self._unconscious_detector.detect, persons, poses, velocity_tracker, config
            )

        if self._enabled.get("abuse") and len(poses) >= 2:
            futures["abuse"] = self._executor.submit(
                self._abuse_detector.detect, persons, poses, velocity_tracker, config
            )

        # Collect results
        fall_events: list[dict[str, Any]] = []
        for name, future in futures.items():
            try:
                results = future.result(timeout=2.0)
                all_threats.extend(results)
                if name == "fall":
                    fall_events = results
            except Exception as e:
                logger.error(f"Detector '{name}' error: {e}")

        # Trespass (needs zone_manager, not parallel with others)
        if self._enabled.get("trespass") and persons:
            try:
                trespass_threats = self._trespass_detector.detect(
                    persons, self._zone_manager, config
                )
                all_threats.extend(trespass_threats)
            except Exception as e:
                logger.error(f"Trespass detector error: {e}")

        # Crowd panic & accident (depend on fall results)
        if self._enabled.get("crowd_panic"):
            try:
                panic_threats = self._crowd_panic_detector.detect(
                    persons, poses, flow_result, fall_events, config
                )
                all_threats.extend(panic_threats)
            except Exception as e:
                logger.error(f"Crowd panic detector error: {e}")

        if self._enabled.get("accident"):
            try:
                accident_threats = self._accident_detector.detect(
                    persons, poses, flow_result, fall_events, config
                )
                all_threats.extend(accident_threats)
            except Exception as e:
                logger.error(f"Accident detector error: {e}")

        # Apply cooldowns
        filtered_threats = self._apply_cooldowns(all_threats, camera_id, timestamp)

        # Convert to ThreatEvent objects
        threat_events = [
            ThreatEvent(
                threat_type=t["threat_type"],
                confidence=t["confidence"],
                persons_involved=t.get("persons_involved", 0),
                person_ids=t.get("person_ids", []),
                location_bbox=t.get("location_bbox", (0, 0, 0, 0)),
                description=t.get("description", ""),
                severity=t.get("severity", "MEDIUM"),
                timestamp=timestamp,
            )
            for t in filtered_threats
        ]

        risk_level = self.get_risk_level(threat_events)

        # Annotate frame
        annotated_frame = None
        if frame is not None:
            annotated_frame = self._draw_threat_overlays(frame, threat_events, risk_level)

        report = ThreatReport(
            camera_id=camera_id,
            timestamp=timestamp,
            threats_detected=threat_events,
            annotated_frame=annotated_frame,
            overall_risk_level=risk_level,
        )

        if threat_events:
            logger.warning(
                f"[{camera_id}] {len(threat_events)} threats detected, "
                f"risk={risk_level}: {[t.threat_type for t in threat_events]}"
            )

        return report

    def _apply_cooldowns(
        self,
        threats: list[dict[str, Any]],
        camera_id: str,
        timestamp: float,
    ) -> list[dict[str, Any]]:
        """Filter threats based on cooldown period."""
        filtered = []
        with self._lock:
            for threat in threats:
                key = (camera_id, threat["threat_type"])
                last_time = self._cooldowns.get(key, 0)

                if timestamp - last_time >= self._cooldown_seconds:
                    filtered.append(threat)
                    self._cooldowns[key] = timestamp

        return filtered

    def get_risk_level(self, threats: list[ThreatEvent]) -> str:
        """Determine overall risk level from detected threats."""
        if not threats:
            return "SAFE"

        max_severity = "SAFE"
        for threat in threats:
            if self.SEVERITY_ORDER.get(threat.severity, 0) > self.SEVERITY_ORDER.get(max_severity, 0):
                max_severity = threat.severity

        return max_severity

    def _draw_threat_overlays(
        self,
        frame: np.ndarray,
        threats: list[ThreatEvent],
        risk_level: str,
    ) -> np.ndarray:
        """Draw threat overlays on frame with colored borders."""
        annotated = frame.copy()
        h, w = annotated.shape[:2]
        border_color = self.SEVERITY_COLORS.get(risk_level, (0, 255, 0))

        # Draw border
        border_thickness = 4 if risk_level in ("HIGH", "CRITICAL") else 2
        cv2.rectangle(annotated, (0, 0), (w - 1, h - 1), border_color, border_thickness)

        # Draw risk level badge
        badge_colors = {
            "SAFE": (0, 150, 0),
            "LOW": (0, 200, 200),
            "MEDIUM": (0, 140, 255),
            "HIGH": (0, 0, 220),
            "CRITICAL": (100, 0, 180),
        }
        badge_color = badge_colors.get(risk_level, (0, 0, 0))
        cv2.rectangle(annotated, (w - 140, 5), (w - 5, 30), badge_color, -1)
        cv2.putText(
            annotated,
            f"RISK: {risk_level}",
            (w - 135, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        # Draw threat labels
        y_offset = 50
        for threat in threats:
            color = self.SEVERITY_COLORS.get(threat.severity, (0, 0, 255))

            # Draw location bbox
            x1, y1, x2, y2 = threat.location_bbox
            if x2 > x1 and y2 > y1:
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{threat.threat_type.upper()} {threat.confidence:.0%}"
            cv2.rectangle(annotated, (5, y_offset - 18), (5 + len(label) * 10, y_offset + 4), color, -1)
            cv2.putText(
                annotated,
                label,
                (8, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
            y_offset += 28

        return annotated

    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self._executor.shutdown(wait=False)
        logger.info("ThreatEngine shutdown")
