"""
SafeWatch — Abuse Detector
Detects sustained physical abuse patterns over extended observation periods.
"""

from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class AbuseDetector:
    """Detects sustained abuse patterns — repeated strikes with dominant/defensive roles."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.80)
        self._skeleton_analyzer = SkeletonAnalyzer()
        self._pair_strike_windows: dict[tuple[int, int], list[int]] = defaultdict(list)
        self._pair_frame_count: dict[tuple[int, int], int] = defaultdict(int)
        self._pair_dominant: dict[tuple[int, int], int] = defaultdict(int)
        self._window_size = 30
        self._min_observation_frames = 120
        logger.info("AbuseDetector initialized")

    def __repr__(self) -> str:
        return f"AbuseDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect abuse events."""
        if len(poses) < 2:
            return []

        threats: list[dict[str, Any]] = []

        for i, p1 in enumerate(poses):
            for j, p2 in enumerate(poses):
                if i >= j:
                    continue

                pair = (min(p1.person_id, p2.person_id), max(p1.person_id, p2.person_id))
                self._pair_frame_count[pair] += 1

                event = self._evaluate_pair(pair, p1, p2, velocity_tracker)
                if event is not None:
                    threats.append(event)

        return threats

    def _evaluate_pair(
        self,
        pair: tuple[int, int],
        pose1: PoseResult,
        pose2: PoseResult,
        velocity_tracker: VelocityTracker,
    ) -> Optional[dict[str, Any]]:
        """Evaluate a pair for sustained abuse pattern."""
        dist = self._skeleton_analyzer.get_inter_person_distance(pose1, pose2)
        if dist is None or dist > 0.4:
            return None

        # Detect strike motion this frame
        wrist_vel_1 = max(
            velocity_tracker.get_velocity(pose1.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose1.person_id, "right_wrist"),
        )
        wrist_vel_2 = max(
            velocity_tracker.get_velocity(pose2.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose2.person_id, "right_wrist"),
        )

        strike_threshold = 30.0
        is_strike = False
        dominant_id = -1

        if wrist_vel_1 > strike_threshold or wrist_vel_2 > strike_threshold:
            is_strike = True
            if wrist_vel_1 > wrist_vel_2:
                dominant_id = pose1.person_id
            else:
                dominant_id = pose2.person_id

        if is_strike:
            frame_num = self._pair_frame_count[pair]
            self._pair_strike_windows[pair].append(frame_num)
            if dominant_id >= 0:
                self._pair_dominant[pair] = dominant_id

        # Only evaluate after enough observation
        if self._pair_frame_count[pair] < self._min_observation_frames:
            return None

        # Count strikes in recent windows
        strikes = self._pair_strike_windows[pair]
        current_frame = self._pair_frame_count[pair]

        # Keep only recent strikes
        recent_strikes = [s for s in strikes if current_frame - s < self._min_observation_frames]
        self._pair_strike_windows[pair] = recent_strikes

        if len(recent_strikes) < 3:
            return None

        # Calculate strike frequency
        strike_freq = len(recent_strikes) / max(1, self._min_observation_frames / self._window_size)

        # Check for victim's learned helplessness posture
        victim_id = pair[0] if self._pair_dominant.get(pair) == pair[1] else pair[1]
        victim_pose = pose1 if pose1.person_id == victim_id else pose2

        helplessness_score = 0.0
        victim_lean = self._skeleton_analyzer.get_body_lean_angle(victim_pose)
        if victim_lean is not None and victim_lean > 20:
            helplessness_score += 0.3

        victim_arm = self._skeleton_analyzer.get_arm_raise_level(victim_pose)
        if victim_arm is not None and victim_arm < 0.2:
            helplessness_score += 0.2

        orientation = self._skeleton_analyzer.get_body_orientation(victim_pose)
        if orientation in ("crouching", "sitting"):
            helplessness_score += 0.2

        # Score
        score = 0.0
        score += min(0.4, strike_freq * 0.1)  # Frequency component
        score += helplessness_score * 0.4      # Victim posture component
        score += 0.2                           # Duration component (already past min frames)

        if score >= self._confidence_threshold:
            severity = "CRITICAL" if score > 0.9 or len(recent_strikes) > 10 else "HIGH"
            dominant = self._pair_dominant.get(pair, pair[0])

            return {
                "threat_type": "abuse",
                "confidence": round(min(1.0, score), 3),
                "persons_involved": 2,
                "person_ids": list(pair),
                "location_bbox": self._get_combined_bbox(pose1, pose2),
                "description": (
                    f"Sustained abuse detected: Person {dominant} (dominant) "
                    f"against Person {victim_id} (victim). "
                    f"{len(recent_strikes)} strike events in "
                    f"{self._pair_frame_count[pair]} frames. "
                    f"Victim helplessness score: {helplessness_score:.2f}"
                ),
                "severity": severity,
            }

        return None

    def _get_combined_bbox(
        self, pose1: PoseResult, pose2: PoseResult
    ) -> tuple[int, int, int, int]:
        x1 = min(pose1.bbox[0], pose2.bbox[0])
        y1 = min(pose1.bbox[1], pose2.bbox[1])
        x2 = max(pose1.bbox[2], pose2.bbox[2])
        y2 = max(pose1.bbox[3], pose2.bbox[3])
        return (x1, y1, x2, y2)
