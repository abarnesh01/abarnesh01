"""
SafeWatch — Harassment Detector
Detects sustained close proximity, cornering, and aggressive gesturing.
"""

import time
from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class HarassmentDetector:
    """Detects harassment based on sustained proximity and behavioral asymmetry."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.75)
        self._proximity_threshold = config.get("proximity_threshold", 0.15)
        self._duration_frames = config.get("duration_frames", 60)
        self._skeleton_analyzer = SkeletonAnalyzer()
        self._pair_proximity_count: dict[tuple[int, int], int] = defaultdict(int)
        self._pair_first_seen: dict[tuple[int, int], float] = {}
        logger.info("HarassmentDetector initialized")

    def __repr__(self) -> str:
        return f"HarassmentDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect harassment events."""
        threats: list[dict[str, Any]] = []

        current_pairs: set[tuple[int, int]] = set()

        for i, p1 in enumerate(poses):
            for j, p2 in enumerate(poses):
                if i >= j:
                    continue

                pair = (min(p1.person_id, p2.person_id), max(p1.person_id, p2.person_id))
                distance = self._skeleton_analyzer.get_inter_person_distance(p1, p2)

                if distance is None:
                    continue

                if distance < self._proximity_threshold:
                    current_pairs.add(pair)
                    self._pair_proximity_count[pair] += 1

                    if pair not in self._pair_first_seen:
                        self._pair_first_seen[pair] = time.time()

                    if self._pair_proximity_count[pair] >= self._duration_frames:
                        score = self._evaluate_harassment(p1, p2, velocity_tracker, distance)

                        if score >= self._confidence_threshold:
                            is_cornered = self._check_cornered(p1, p2)
                            severity = "HIGH" if is_cornered else "MEDIUM"

                            threats.append({
                                "threat_type": "harassment",
                                "confidence": round(score, 3),
                                "persons_involved": 2,
                                "person_ids": list(pair),
                                "location_bbox": self._get_combined_bbox(p1, p2),
                                "description": (
                                    f"Sustained close proximity between Person {pair[0]} "
                                    f"and Person {pair[1]} for "
                                    f"{self._pair_proximity_count[pair]} frames. "
                                    f"{'Victim appears cornered. ' if is_cornered else ''}"
                                    f"Distance: {distance:.3f}"
                                ),
                                "severity": severity,
                            })

        # Decay proximity count for pairs no longer close
        stale_pairs = [p for p in self._pair_proximity_count if p not in current_pairs]
        for pair in stale_pairs:
            self._pair_proximity_count[pair] = max(0, self._pair_proximity_count[pair] - 2)
            if self._pair_proximity_count[pair] == 0:
                self._pair_proximity_count.pop(pair, None)
                self._pair_first_seen.pop(pair, None)

        return threats

    def _evaluate_harassment(
        self,
        pose1: PoseResult,
        pose2: PoseResult,
        velocity_tracker: VelocityTracker,
        distance: float,
    ) -> float:
        """Evaluate harassment probability for a pair."""
        score = 0.0

        # 1. Sustained proximity (already confirmed)
        score += 0.3

        # 2. Movement asymmetry: one stationary, other approaching
        vel1 = velocity_tracker.get_average_velocity(pose1.person_id, n_frames=5)
        vel2 = velocity_tracker.get_average_velocity(pose2.person_id, n_frames=5)

        if vel1 > 0.01 and vel2 < 0.005:
            score += 0.2
        elif vel2 > 0.01 and vel1 < 0.005:
            score += 0.2

        # 3. Body orientation asymmetry
        lean1 = self._skeleton_analyzer.get_body_lean_angle(pose1)
        lean2 = self._skeleton_analyzer.get_body_lean_angle(pose2)
        if lean1 is not None and lean2 is not None:
            if abs(lean1 - lean2) > 20:
                score += 0.15

        # 4. Aggressive arm gesturing
        arm1 = self._skeleton_analyzer.get_arm_raise_level(pose1)
        arm2 = self._skeleton_analyzer.get_arm_raise_level(pose2)
        if arm1 is not None and arm2 is not None:
            if arm1 > 0.5 and arm2 < 0.2:
                score += 0.2
            elif arm2 > 0.5 and arm1 < 0.2:
                score += 0.2

        # 5. Cornering bonus
        if self._check_cornered(pose1, pose2):
            score += 0.15

        return min(1.0, score)

    def _check_cornered(self, pose1: PoseResult, pose2: PoseResult) -> bool:
        """Check if one person appears to be cornered (near frame edges)."""
        for pose in [pose1, pose2]:
            com = self._skeleton_analyzer.get_center_of_mass(pose)
            if com is not None:
                x, y = com
                if x < 0.05 or x > 0.95 or y < 0.05 or y > 0.95:
                    return True
        return False

    def _get_combined_bbox(
        self, pose1: PoseResult, pose2: PoseResult
    ) -> tuple[int, int, int, int]:
        x1 = min(pose1.bbox[0], pose2.bbox[0])
        y1 = min(pose1.bbox[1], pose2.bbox[1])
        x2 = max(pose1.bbox[2], pose2.bbox[2])
        y2 = max(pose1.bbox[3], pose2.bbox[3])
        return (x1, y1, x2, y2)
