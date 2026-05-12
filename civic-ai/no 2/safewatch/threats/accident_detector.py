"""
SafeWatch — Accident Detector
Detects accidents via multiple falls, sudden motion spikes, and crowd reactions.
"""

from collections import deque
from typing import Any, Optional

import numpy as np
from loguru import logger

from detection.optical_flow import FlowResult
from detection.pose_estimator import PoseResult


class AccidentDetector:
    """Detects accidents from correlated falls, motion spikes, and sudden changes."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.78)
        self._fall_history: deque[dict[str, Any]] = deque(maxlen=60)
        self._flow_history: deque[float] = deque(maxlen=30)
        self._person_count_history: deque[int] = deque(maxlen=30)
        logger.info("AccidentDetector initialized")

    def __repr__(self) -> str:
        return f"AccidentDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        flow_result: Optional[FlowResult],
        fall_events: list[dict[str, Any]],
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect accident events."""
        threats: list[dict[str, Any]] = []

        # Track fall events
        for fall in fall_events:
            self._fall_history.append(fall)

        # Track flow magnitude
        if flow_result is not None:
            self._flow_history.append(flow_result.mean_magnitude)

        # Track person count
        self._person_count_history.append(len(persons))

        score = 0.0
        evidence: list[str] = []

        # 1. Multiple falls within recent window (30 frames)
        recent_falls = list(self._fall_history)[-30:]
        unique_fallen = set()
        for f in recent_falls:
            for pid in f.get("person_ids", []):
                unique_fallen.add(pid)

        if len(unique_fallen) >= 2:
            fall_score = min(1.0, len(unique_fallen) / 4.0)
            score += fall_score * 0.4
            evidence.append(f"{len(unique_fallen)} persons fell recently")

        # 2. Motion spike followed by stillness
        if len(self._flow_history) >= 10:
            flow_list = list(self._flow_history)
            first_half = flow_list[:len(flow_list)//2]
            second_half = flow_list[len(flow_list)//2:]

            if first_half and second_half:
                avg_first = np.mean(first_half)
                avg_second = np.mean(second_half)

                if avg_first > 8.0 and avg_second < 3.0:
                    score += 0.25
                    evidence.append("Motion spike then stillness")

        # 3. Sudden person count change (people fleeing)
        if len(self._person_count_history) >= 10:
            counts = list(self._person_count_history)
            recent_change = abs(counts[-1] - counts[-10]) if len(counts) >= 10 else 0
            if recent_change >= 3:
                score += 0.2
                evidence.append(f"Person count changed by {recent_change}")

        # 4. High flow combined with falls
        if flow_result and flow_result.max_magnitude > 15.0 and len(unique_fallen) >= 1:
            score += 0.15
            evidence.append("High motion with falls")

        if score >= self._confidence_threshold:
            num_involved = max(len(unique_fallen), 2)
            severity = "CRITICAL" if num_involved >= 3 else "HIGH"
            threats.append({
                "threat_type": "accident",
                "confidence": round(min(1.0, score), 3),
                "persons_involved": num_involved,
                "person_ids": list(unique_fallen),
                "location_bbox": self._get_scene_bbox(persons),
                "description": (
                    f"Accident detected involving {num_involved} persons. "
                    f"Evidence: {'; '.join(evidence)}"
                ),
                "severity": severity,
            })

        return threats

    def _get_scene_bbox(self, persons: list) -> tuple[int, int, int, int]:
        """Get bounding box covering the scene."""
        if not persons:
            return (0, 0, 640, 480)
        x1 = min(p.bbox[0] for p in persons)
        y1 = min(p.bbox[1] for p in persons)
        x2 = max(p.bbox[2] for p in persons)
        y2 = max(p.bbox[3] for p in persons)
        return (x1, y1, x2, y2)
