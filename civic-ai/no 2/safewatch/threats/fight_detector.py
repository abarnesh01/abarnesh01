"""
SafeWatch — Fight Detector
Detects physical fights between multiple persons.
"""

from typing import Any

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class FightDetector:
    """Detects physical fights between people using pose and velocity analysis."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.82)
        self._min_persons = config.get("min_persons", 2)
        self._velocity_threshold = config.get("velocity_threshold", 45.0)
        self._overlap_threshold = config.get("overlap_threshold", 0.3)
        self._skeleton_analyzer = SkeletonAnalyzer()
        logger.info("FightDetector initialized")

    def __repr__(self) -> str:
        return f"FightDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect fight events. Returns list of ThreatEvent dicts."""
        if len(persons) < self._min_persons:
            return []

        threats: list[dict[str, Any]] = []
        checked_pairs: set[tuple[int, int]] = set()

        for i, p1 in enumerate(poses):
            for j, p2 in enumerate(poses):
                if i >= j:
                    continue

                pair = (min(p1.person_id, p2.person_id), max(p1.person_id, p2.person_id))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                score = self._evaluate_fight_pair(p1, p2, velocity_tracker)

                if score >= self._confidence_threshold:
                    severity = "CRITICAL" if score > 0.92 else "HIGH"
                    threats.append({
                        "threat_type": "fight",
                        "confidence": round(score, 3),
                        "persons_involved": 2,
                        "person_ids": list(pair),
                        "location_bbox": self._get_combined_bbox(p1, p2),
                        "description": (
                            f"Physical fight detected between Person {pair[0]} "
                            f"and Person {pair[1]}. Confidence: {score:.0%}"
                        ),
                        "severity": severity,
                    })

        return threats

    def _evaluate_fight_pair(
        self,
        pose1: PoseResult,
        pose2: PoseResult,
        velocity_tracker: VelocityTracker,
    ) -> float:
        """Evaluate fight probability for a pair of persons."""
        signals: list[float] = []
        weights: list[float] = []

        # 1. Proximity check
        dist = self._skeleton_analyzer.get_inter_person_distance(pose1, pose2)
        if dist is not None:
            proximity_score = max(0.0, 1.0 - dist / 0.3)
            signals.append(proximity_score)
            weights.append(0.2)
        else:
            return 0.0

        if dist is not None and dist > 0.4:
            return 0.0

        # 2. Relative velocity (closing speed)
        rel_vel = velocity_tracker.get_relative_velocity(pose1.person_id, pose2.person_id)
        vel_score = min(1.0, abs(rel_vel) / self._velocity_threshold) if self._velocity_threshold > 0 else 0.0
        signals.append(vel_score)
        weights.append(0.2)

        # 3. Arm raise level for both
        arm1 = self._skeleton_analyzer.get_arm_raise_level(pose1)
        arm2 = self._skeleton_analyzer.get_arm_raise_level(pose2)
        arm_score = 0.0
        if arm1 is not None and arm2 is not None:
            arm_score = (arm1 + arm2) / 2.0
        elif arm1 is not None:
            arm_score = arm1 * 0.5
        elif arm2 is not None:
            arm_score = arm2 * 0.5
        signals.append(arm_score)
        weights.append(0.2)

        # 4. Wrist velocity (striking motion)
        wrist_vel_1 = max(
            velocity_tracker.get_velocity(pose1.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose1.person_id, "right_wrist"),
        )
        wrist_vel_2 = max(
            velocity_tracker.get_velocity(pose2.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose2.person_id, "right_wrist"),
        )
        max_wrist = max(wrist_vel_1, wrist_vel_2)
        wrist_score = min(1.0, max_wrist / self._velocity_threshold) if self._velocity_threshold > 0 else 0.0
        signals.append(wrist_score)
        weights.append(0.25)

        # 5. Body lean toward each other
        lean1 = self._skeleton_analyzer.get_body_lean_angle(pose1)
        lean2 = self._skeleton_analyzer.get_body_lean_angle(pose2)
        lean_score = 0.0
        if lean1 is not None and lean2 is not None:
            lean_score = min(1.0, (lean1 + lean2) / 80.0)
        signals.append(lean_score)
        weights.append(0.15)

        # Weighted average
        if not signals or sum(weights) == 0:
            return 0.0

        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(signals, weights))
        confidence = weighted_sum / total_weight

        return float(confidence)

    def _get_combined_bbox(
        self, pose1: PoseResult, pose2: PoseResult
    ) -> tuple[int, int, int, int]:
        """Get combined bounding box covering both persons."""
        x1 = min(pose1.bbox[0], pose2.bbox[0])
        y1 = min(pose1.bbox[1], pose2.bbox[1])
        x2 = max(pose1.bbox[2], pose2.bbox[2])
        y2 = max(pose1.bbox[3], pose2.bbox[3])
        return (x1, y1, x2, y2)
