"""
SafeWatch — Fall Detector
Detects sudden falls, gradual collapses, and slip-and-fall events.
"""

import time
from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class FallDetector:
    """State-machine based fall detector with multi-stage classification."""

    STANDING = "STANDING"
    FALLING = "FALLING"
    FALLEN = "FALLEN"
    STATIONARY_FALLEN = "STATIONARY_FALLEN"

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.78)
        self._hip_drop_threshold = config.get("hip_drop_threshold", 80)
        self._stillness_frames = config.get("stillness_frames", 30)
        self._skeleton_analyzer = SkeletonAnalyzer()
        self._person_states: dict[int, str] = defaultdict(lambda: self.STANDING)
        self._fallen_frame_count: dict[int, int] = defaultdict(int)
        self._hip_history: dict[int, list[float]] = defaultdict(list)
        self._max_hip_history = 30
        logger.info("FallDetector initialized")

    def __repr__(self) -> str:
        return f"FallDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect fall events. Returns list of ThreatEvent dicts."""
        threats: list[dict[str, Any]] = []

        for pose in poses:
            pid = pose.person_id
            event = self._evaluate_person(pose, velocity_tracker)
            if event is not None:
                threats.append(event)

        return threats

    def _evaluate_person(
        self,
        pose: PoseResult,
        velocity_tracker: VelocityTracker,
    ) -> Optional[dict[str, Any]]:
        """Evaluate a single person for fall state transitions."""
        pid = pose.person_id
        state = self._person_states[pid]

        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")

        if l_hip and r_hip:
            hip_y = (l_hip.y + r_hip.y) / 2.0
            self._hip_history[pid].append(hip_y)
            if len(self._hip_history[pid]) > self._max_hip_history:
                self._hip_history[pid] = self._hip_history[pid][-self._max_hip_history:]
        else:
            return None

        is_horizontal = self._skeleton_analyzer.is_person_horizontal(pose, threshold=25)
        hip_drop_speed = self._get_hip_drop_speed(pid)
        avg_vel = velocity_tracker.get_average_velocity(pid, n_frames=5)

        if state == self.STANDING:
            if hip_drop_speed > 0.05 and is_horizontal:
                self._person_states[pid] = self.FALLING
                self._fallen_frame_count[pid] = 0
            elif hip_drop_speed > 0.08:
                self._person_states[pid] = self.FALLING
                self._fallen_frame_count[pid] = 0

        elif state == self.FALLING:
            if is_horizontal:
                self._person_states[pid] = self.FALLEN
                self._fallen_frame_count[pid] = 0
                confidence = min(1.0, 0.6 + hip_drop_speed * 3.0)
                if confidence >= self._confidence_threshold:
                    return {
                        "threat_type": "fall",
                        "confidence": round(confidence, 3),
                        "persons_involved": 1,
                        "person_ids": [pid],
                        "location_bbox": pose.bbox,
                        "description": (
                            f"Person {pid} has fallen. "
                            f"Hip drop velocity: {hip_drop_speed:.3f}. "
                            f"Monitoring for stillness."
                        ),
                        "severity": "MEDIUM",
                    }
            elif avg_vel > 0.02:
                self._person_states[pid] = self.STANDING

        elif state == self.FALLEN:
            if is_horizontal and avg_vel < 0.005:
                self._fallen_frame_count[pid] += 1
                if self._fallen_frame_count[pid] >= self._stillness_frames:
                    self._person_states[pid] = self.STATIONARY_FALLEN
                    return {
                        "threat_type": "fall",
                        "confidence": 0.92,
                        "persons_involved": 1,
                        "person_ids": [pid],
                        "location_bbox": pose.bbox,
                        "description": (
                            f"Person {pid} has been on the ground and motionless "
                            f"for {self._fallen_frame_count[pid]} frames. "
                            f"Possible injury or unconsciousness."
                        ),
                        "severity": "HIGH",
                    }
            elif not is_horizontal:
                self._person_states[pid] = self.STANDING
                self._fallen_frame_count[pid] = 0

        elif state == self.STATIONARY_FALLEN:
            if not is_horizontal or avg_vel > 0.01:
                self._person_states[pid] = self.STANDING
                self._fallen_frame_count[pid] = 0
            else:
                self._fallen_frame_count[pid] += 1

        return None

    def _get_hip_drop_speed(self, person_id: int) -> float:
        """Calculate how fast the hips are dropping (positive = downward)."""
        history = self._hip_history.get(person_id, [])
        if len(history) < 3:
            return 0.0

        recent = history[-5:]
        if len(recent) < 2:
            return 0.0

        drop = recent[-1] - recent[0]
        return max(0.0, float(drop))

    def get_person_state(self, person_id: int) -> str:
        """Get the current state of a person."""
        return self._person_states.get(person_id, self.STANDING)
