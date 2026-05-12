"""
SafeWatch — Assault Detector
Detects one-sided physical assault with victim/assailant role assignment.
"""

from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.velocity_tracker import VelocityTracker
from detection.pose_estimator import PoseResult


class AssaultDetector:
    """Detects physical assault — more aggressive/one-sided than fight detection."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.85)
        self._strike_velocity_threshold = config.get("strike_velocity_threshold", 60.0)
        self._skeleton_analyzer = SkeletonAnalyzer()
        self._strike_count: dict[tuple[int, int], int] = defaultdict(int)
        logger.info("AssaultDetector initialized")

    def __repr__(self) -> str:
        return f"AssaultDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list,
        poses: list[PoseResult],
        velocity_tracker: VelocityTracker,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect assault events."""
        if len(poses) < 2:
            return []

        threats: list[dict[str, Any]] = []

        for i, p1 in enumerate(poses):
            for j, p2 in enumerate(poses):
                if i >= j:
                    continue

                result = self._evaluate_assault_pair(p1, p2, velocity_tracker)
                if result is not None:
                    threats.append(result)

        return threats

    def _evaluate_assault_pair(
        self,
        pose1: PoseResult,
        pose2: PoseResult,
        velocity_tracker: VelocityTracker,
    ) -> Optional[dict[str, Any]]:
        """Evaluate assault between a pair, assign assailant/victim roles."""
        dist = self._skeleton_analyzer.get_inter_person_distance(pose1, pose2)
        if dist is None or dist > 0.35:
            return None

        # Determine aggressor by wrist velocity
        max_wrist_vel_1 = max(
            velocity_tracker.get_velocity(pose1.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose1.person_id, "right_wrist"),
        )
        max_wrist_vel_2 = max(
            velocity_tracker.get_velocity(pose2.person_id, "left_wrist"),
            velocity_tracker.get_velocity(pose2.person_id, "right_wrist"),
        )

        if max_wrist_vel_1 > max_wrist_vel_2:
            assailant, victim = pose1, pose2
            attack_vel = max_wrist_vel_1
        else:
            assailant, victim = pose2, pose1
            attack_vel = max_wrist_vel_2

        score = 0.0

        # 1. High wrist velocity from attacker
        if self._strike_velocity_threshold > 0:
            vel_score = min(1.0, attack_vel / self._strike_velocity_threshold)
        else:
            vel_score = 0.0
        score += vel_score * 0.3

        # 2. Victim retreating/stationary
        victim_vel = velocity_tracker.get_average_velocity(victim.person_id, n_frames=5)
        attacker_vel = velocity_tracker.get_average_velocity(assailant.person_id, n_frames=5)
        if attacker_vel > victim_vel * 2 and victim_vel < 0.02:
            score += 0.2

        # 3. Victim evasive (cowering — low body angle)
        victim_lean = self._skeleton_analyzer.get_body_lean_angle(victim)
        if victim_lean is not None and victim_lean > 30:
            score += 0.15

        # 4. Victim arm orientation (defensive — arms raised to block)
        victim_arm = self._skeleton_analyzer.get_arm_raise_level(victim)
        attacker_arm = self._skeleton_analyzer.get_arm_raise_level(assailant)
        if victim_arm is not None and attacker_arm is not None:
            if attacker_arm > 0.6 and victim_arm > 0.3:
                score += 0.15

        # 5. Arm extension toward victim (strike motion)
        for limb in ["left_arm", "right_arm"]:
            ext = self._skeleton_analyzer.get_limb_extension(assailant, limb)
            if ext is not None and ext > 0.85:
                score += 0.1
                break

        # 6. Track repeated strikes
        pair_key = (min(assailant.person_id, victim.person_id),
                    max(assailant.person_id, victim.person_id))
        if attack_vel > self._strike_velocity_threshold * 0.5:
            self._strike_count[pair_key] += 1

        if self._strike_count[pair_key] > 3:
            score += 0.1

        if score >= self._confidence_threshold:
            return {
                "threat_type": "assault",
                "confidence": round(min(1.0, score), 3),
                "persons_involved": 2,
                "person_ids": [assailant.person_id, victim.person_id],
                "location_bbox": self._get_combined_bbox(assailant, victim),
                "description": (
                    f"Assault detected: Person {assailant.person_id} (assailant) "
                    f"attacking Person {victim.person_id} (victim). "
                    f"Strike velocity: {attack_vel:.1f}, "
                    f"Strikes counted: {self._strike_count[pair_key]}"
                ),
                "severity": "CRITICAL",
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
