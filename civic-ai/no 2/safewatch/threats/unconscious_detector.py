"""
SafeWatch — Unconscious Detector
Detects persons who are horizontal and motionless for extended periods.
"""

from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class UnconsciousDetector:
    """Detects unconscious persons via horizontal pose and extended stillness."""

    ACTIVE = "ACTIVE"
    FALLEN = "FALLEN"
    POSSIBLY_UNCONSCIOUS = "POSSIBLY_UNCONSCIOUS"
    UNCONSCIOUS = "UNCONSCIOUS"

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.80)
        self._horizontal_angle_threshold = config.get("horizontal_angle_threshold", 25)
        self._stillness_frames = config.get("stillness_frames", 90)
        self._pass_away_frames = config.get("stillness_frames", 90) * 2
        self._skeleton_analyzer = SkeletonAnalyzer()
        self._person_states: dict[int, str] = defaultdict(lambda: self.ACTIVE)
        self._stillness_count: dict[int, int] = defaultdict(int)
        self._had_initial_fall: dict[int, bool] = defaultdict(bool)
        logger.info("UnconsciousDetector initialized")

    def __repr__(self) -> str:
        return f"UnconsciousDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect unconscious events."""
        threats: list[dict[str, Any]] = []

        for pose in poses:
            event = self._evaluate_person(pose, velocity_tracker)
            if event is not None:
                threats.append(event)

        return threats

    def _evaluate_person(
        self,
        pose: PoseResult,
        velocity_tracker: VelocityTracker,
    ) -> Optional[dict[str, Any]]:
        """Evaluate a single person for unconsciousness."""
        pid = pose.person_id
        state = self._person_states[pid]

        is_horizontal = self._skeleton_analyzer.is_person_horizontal(
            pose, threshold=self._horizontal_angle_threshold
        )
        avg_vel = velocity_tracker.get_average_velocity(pid, n_frames=5)
        is_still = avg_vel < 0.003

        # Check head at ground level
        nose = pose.get_landmark("nose")
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")
        head_at_ground = False
        if nose and l_hip and r_hip:
            hip_y = (l_hip.y + r_hip.y) / 2.0
            head_at_ground = nose.y >= hip_y - 0.02

        if state == self.ACTIVE:
            if is_horizontal:
                self._person_states[pid] = self.FALLEN
                self._stillness_count[pid] = 0
                self._had_initial_fall[pid] = True

        elif state == self.FALLEN:
            if is_horizontal and is_still:
                self._stillness_count[pid] += 1
                if self._stillness_count[pid] >= self._stillness_frames // 2:
                    self._person_states[pid] = self.POSSIBLY_UNCONSCIOUS
                    return {
                        "threat_type": "unconscious",
                        "confidence": 0.75,
                        "persons_involved": 1,
                        "person_ids": [pid],
                        "location_bbox": pose.bbox,
                        "description": (
                            f"Person {pid} possibly unconscious. "
                            f"Horizontal for {self._stillness_count[pid]} frames. "
                            f"Monitoring continues."
                        ),
                        "severity": "HIGH",
                    }
            elif not is_horizontal:
                self._person_states[pid] = self.ACTIVE
                self._stillness_count[pid] = 0

        elif state == self.POSSIBLY_UNCONSCIOUS:
            if is_horizontal and is_still:
                self._stillness_count[pid] += 1
                if self._stillness_count[pid] >= self._stillness_frames:
                    self._person_states[pid] = self.UNCONSCIOUS
                    return {
                        "threat_type": "unconscious",
                        "confidence": 0.92,
                        "persons_involved": 1,
                        "person_ids": [pid],
                        "location_bbox": pose.bbox,
                        "description": (
                            f"Person {pid} confirmed unconscious. "
                            f"Motionless and horizontal for {self._stillness_count[pid]} frames. "
                            f"Head at ground level: {head_at_ground}."
                        ),
                        "severity": "CRITICAL",
                    }
            elif not is_horizontal or not is_still:
                self._person_states[pid] = self.ACTIVE
                self._stillness_count[pid] = 0

        elif state == self.UNCONSCIOUS:
            if not is_horizontal or not is_still:
                self._person_states[pid] = self.ACTIVE
                self._stillness_count[pid] = 0
            else:
                self._stillness_count[pid] += 1
                if self._stillness_count[pid] >= self._pass_away_frames:
                    return {
                        "threat_type": "pass_away",
                        "confidence": 0.85,
                        "persons_involved": 1,
                        "person_ids": [pid],
                        "location_bbox": pose.bbox,
                        "description": (
                            f"CRITICAL: Person {pid} has been unconscious and motionless "
                            f"for extended period ({self._stillness_count[pid]} frames). "
                            f"Immediate medical attention required."
                        ),
                        "severity": "CRITICAL",
                    }

        return None

    def get_person_state(self, person_id: int) -> str:
        """Get the current state of a person."""
        return self._person_states.get(person_id, self.ACTIVE)
