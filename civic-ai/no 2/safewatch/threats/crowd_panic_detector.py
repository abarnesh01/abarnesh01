"""
SafeWatch — Crowd Panic Detector
Detects crowd panic via optical flow divergence and mass movement analysis.
"""

from collections import deque
from typing import Any, Optional

import numpy as np
from loguru import logger

from detection.optical_flow import FlowResult
from detection.pose_estimator import PoseResult


class CrowdPanicDetector:
    """Detects crowd panic using optical flow divergence and person count analysis."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.72)
        self._flow_divergence_threshold = config.get("flow_divergence_threshold", 8.0)
        self._min_persons = config.get("min_persons", 5)
        self._person_count_history: deque[int] = deque(maxlen=30)
        self._simultaneous_falls = 0
        logger.info("CrowdPanicDetector initialized")

    def __repr__(self) -> str:
        return f"CrowdPanicDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        flow_result: Optional[FlowResult],
        fall_events: list[dict[str, Any]],
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect crowd panic events."""
        threats: list[dict[str, Any]] = []
        num_persons = len(persons)
        self._person_count_history.append(num_persons)

        if num_persons < self._min_persons:
            return []

        score = 0.0
        evidence: list[str] = []

        # 1. Optical flow divergence
        if flow_result is not None:
            if flow_result.divergence_score > self._flow_divergence_threshold:
                div_score = min(1.0, flow_result.divergence_score / (self._flow_divergence_threshold * 2))
                score += div_score * 0.35
                evidence.append(f"Flow divergence: {flow_result.divergence_score:.2f}")

            # High overall motion
            if flow_result.mean_magnitude > 10.0:
                motion_score = min(1.0, flow_result.mean_magnitude / 30.0)
                score += motion_score * 0.15
                evidence.append(f"High motion: {flow_result.mean_magnitude:.2f}")

        # 2. Sudden person count change (people rushing in/out)
        if len(self._person_count_history) >= 5:
            recent = list(self._person_count_history)
            count_velocity = abs(recent[-1] - recent[-5])
            if count_velocity >= 3:
                score += 0.2
                evidence.append(f"Person count change: {count_velocity}")

        # 3. Multiple simultaneous falls
        if len(fall_events) >= 2:
            score += 0.25
            evidence.append(f"Simultaneous falls: {len(fall_events)}")

        # 4. Check if all persons moving away from center
        if len(poses) >= self._min_persons:
            moving_away = self._check_radial_movement(poses)
            if moving_away:
                score += 0.15
                evidence.append("Radial dispersal detected")

        if score >= self._confidence_threshold:
            severity = "CRITICAL" if score > 0.85 else "HIGH"
            threats.append({
                "threat_type": "crowd_panic",
                "confidence": round(min(1.0, score), 3),
                "persons_involved": num_persons,
                "person_ids": [p.id for p in persons],
                "location_bbox": self._get_crowd_bbox(persons),
                "description": (
                    f"Crowd panic detected with {num_persons} persons. "
                    f"Evidence: {'; '.join(evidence)}"
                ),
                "severity": severity,
            })

        return threats

    def _check_radial_movement(self, poses: list[PoseResult]) -> bool:
        """Check if persons are moving away from a common center point."""
        centers = []
        for pose in poses:
            l_hip = pose.get_landmark("left_hip")
            r_hip = pose.get_landmark("right_hip")
            if l_hip and r_hip:
                centers.append(((l_hip.x + r_hip.x) / 2.0, (l_hip.y + r_hip.y) / 2.0))

        if len(centers) < 3:
            return False

        avg_x = np.mean([c[0] for c in centers])
        avg_y = np.mean([c[1] for c in centers])

        distances = [np.sqrt((c[0] - avg_x)**2 + (c[1] - avg_y)**2) for c in centers]
        avg_dist = np.mean(distances)

        return avg_dist > 0.2

    def _get_crowd_bbox(self, persons: list) -> tuple[int, int, int, int]:
        """Get bounding box covering all persons."""
        if not persons:
            return (0, 0, 0, 0)
        x1 = min(p.bbox[0] for p in persons)
        y1 = min(p.bbox[1] for p in persons)
        x2 = max(p.bbox[2] for p in persons)
        y2 = max(p.bbox[3] for p in persons)
        return (x1, y1, x2, y2)
