"""
SafeWatch — Skeleton Analyzer
Behavioral feature extraction from pose landmarks.
"""

from typing import Optional

import numpy as np
from loguru import logger

from detection.pose_estimator import PoseResult


class SkeletonAnalyzer:
    """Extracts behavioral features from pose results."""

    def __init__(self) -> None:
        logger.info("SkeletonAnalyzer initialized")

    def __repr__(self) -> str:
        return "SkeletonAnalyzer()"

    def get_body_orientation(self, pose: PoseResult) -> Optional[str]:
        """Determine body orientation: standing, sitting, lying, crouching."""
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")
        l_knee = pose.get_landmark("left_knee")
        r_knee = pose.get_landmark("right_knee")
        l_shoulder = pose.get_landmark("left_shoulder")
        r_shoulder = pose.get_landmark("right_shoulder")
        nose = pose.get_landmark("nose")

        if l_hip is None or r_hip is None:
            return None

        hip_y = (l_hip.y + r_hip.y) / 2.0

        if l_shoulder and r_shoulder:
            shoulder_y = (l_shoulder.y + r_shoulder.y) / 2.0
            torso_height = abs(shoulder_y - hip_y)

            if torso_height < 0.03:
                return "lying"

            if l_knee and r_knee:
                knee_y = (l_knee.y + r_knee.y) / 2.0
                hip_knee_diff = knee_y - hip_y

                if hip_knee_diff < 0.02:
                    return "sitting"

                if torso_height < 0.08 and hip_knee_diff < 0.05:
                    return "crouching"

        if self.is_person_horizontal(pose, threshold=25):
            return "lying"

        return "standing"

    def get_arm_raise_level(self, pose: PoseResult) -> Optional[float]:
        """Get arm raise level: 0.0 (down) to 1.0 (fully raised)."""
        l_shoulder = pose.get_landmark("left_shoulder")
        r_shoulder = pose.get_landmark("right_shoulder")
        l_wrist = pose.get_landmark("left_wrist")
        r_wrist = pose.get_landmark("right_wrist")
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")

        if l_shoulder is None or r_shoulder is None:
            return None

        shoulder_y = (l_shoulder.y + r_shoulder.y) / 2.0
        hip_y_val = None
        if l_hip and r_hip:
            hip_y_val = (l_hip.y + r_hip.y) / 2.0

        levels = []

        if l_wrist and l_shoulder:
            diff = l_shoulder.y - l_wrist.y
            range_val = (hip_y_val - l_shoulder.y) if hip_y_val else 0.15
            range_val = max(range_val, 0.01)
            level = np.clip(diff / range_val, 0.0, 1.0)
            levels.append(float(level))

        if r_wrist and r_shoulder:
            diff = r_shoulder.y - r_wrist.y
            range_val = (hip_y_val - r_shoulder.y) if hip_y_val else 0.15
            range_val = max(range_val, 0.01)
            level = np.clip(diff / range_val, 0.0, 1.0)
            levels.append(float(level))

        if not levels:
            return None

        return float(max(levels))

    def get_body_lean_angle(self, pose: PoseResult) -> Optional[float]:
        """Get body lean angle from vertical in degrees."""
        l_shoulder = pose.get_landmark("left_shoulder")
        r_shoulder = pose.get_landmark("right_shoulder")
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")

        if not all([l_shoulder, r_shoulder, l_hip, r_hip]):
            return None

        shoulder_mid = np.array([
            (l_shoulder.x + r_shoulder.x) / 2.0,
            (l_shoulder.y + r_shoulder.y) / 2.0,
        ])
        hip_mid = np.array([
            (l_hip.x + r_hip.x) / 2.0,
            (l_hip.y + r_hip.y) / 2.0,
        ])

        torso_vec = shoulder_mid - hip_mid
        vertical = np.array([0.0, -1.0])

        dot = np.dot(torso_vec, vertical)
        mag = np.linalg.norm(torso_vec)

        if mag < 1e-6:
            return None

        cos_angle = np.clip(dot / mag, -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        return float(angle)

    def get_torso_rotation(self, pose: PoseResult) -> Optional[float]:
        """Get torso rotation angle in degrees (twist around vertical axis)."""
        l_shoulder = pose.get_landmark("left_shoulder")
        r_shoulder = pose.get_landmark("right_shoulder")
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")

        if not all([l_shoulder, r_shoulder, l_hip, r_hip]):
            return None

        shoulder_dx = r_shoulder.x - l_shoulder.x
        hip_dx = r_hip.x - l_hip.x

        if abs(shoulder_dx) < 1e-6 or abs(hip_dx) < 1e-6:
            return 0.0

        shoulder_angle = np.degrees(np.arctan2(
            r_shoulder.y - l_shoulder.y,
            shoulder_dx,
        ))
        hip_angle = np.degrees(np.arctan2(
            r_hip.y - l_hip.y,
            hip_dx,
        ))

        rotation = abs(shoulder_angle - hip_angle)
        return float(rotation)

    def get_head_position_relative_to_hips(self, pose: PoseResult) -> Optional[float]:
        """Get normalized Y offset of head relative to hips. Negative = above hips."""
        nose = pose.get_landmark("nose")
        l_hip = pose.get_landmark("left_hip")
        r_hip = pose.get_landmark("right_hip")

        if nose is None or l_hip is None or r_hip is None:
            return None

        hip_y = (l_hip.y + r_hip.y) / 2.0
        offset = nose.y - hip_y
        return float(offset)

    def is_person_horizontal(self, pose: PoseResult, threshold: float = 25.0) -> bool:
        """Check if person is horizontal (lying down). Returns False if landmarks missing."""
        lean_angle = self.get_body_lean_angle(pose)
        if lean_angle is None:
            return False
        return lean_angle > (90.0 - threshold)

    def get_center_of_mass(self, pose: PoseResult) -> Optional[tuple[float, float]]:
        """Get estimated center of mass as normalized (x, y) coordinates."""
        key_joints = [
            "left_shoulder", "right_shoulder",
            "left_hip", "right_hip",
            "left_knee", "right_knee",
        ]
        weights = [1.0, 1.0, 2.0, 2.0, 1.5, 1.5]

        x_sum = 0.0
        y_sum = 0.0
        w_sum = 0.0

        for joint_name, weight in zip(key_joints, weights):
            lm = pose.get_landmark(joint_name)
            if lm is not None:
                x_sum += lm.x * weight
                y_sum += lm.y * weight
                w_sum += weight

        if w_sum < 1e-6:
            return None

        return (x_sum / w_sum, y_sum / w_sum)

    def get_limb_extension(self, pose: PoseResult, limb: str) -> Optional[float]:
        """Get limb extension ratio (0.0=fully bent to 1.0=fully extended).
        
        Supported limbs: left_arm, right_arm, left_leg, right_leg.
        """
        limb_joints = {
            "left_arm": ("left_shoulder", "left_elbow", "left_wrist"),
            "right_arm": ("right_shoulder", "right_elbow", "right_wrist"),
            "left_leg": ("left_hip", "left_knee", "left_ankle"),
            "right_leg": ("right_hip", "right_knee", "right_ankle"),
        }

        joints = limb_joints.get(limb)
        if joints is None:
            return None

        j1 = pose.get_landmark(joints[0])
        j2 = pose.get_landmark(joints[1])
        j3 = pose.get_landmark(joints[2])

        if any(j is None for j in [j1, j2, j3]):
            return None

        seg1 = np.sqrt((j2.x - j1.x) ** 2 + (j2.y - j1.y) ** 2)
        seg2 = np.sqrt((j3.x - j2.x) ** 2 + (j3.y - j2.y) ** 2)
        total_length = seg1 + seg2

        if total_length < 1e-6:
            return None

        direct_dist = np.sqrt((j3.x - j1.x) ** 2 + (j3.y - j1.y) ** 2)
        extension = direct_dist / total_length

        return float(np.clip(extension, 0.0, 1.0))

    def get_inter_person_distance(
        self, pose1: PoseResult, pose2: PoseResult
    ) -> Optional[float]:
        """Get normalized distance between two persons' centers of mass."""
        com1 = self.get_center_of_mass(pose1)
        com2 = self.get_center_of_mass(pose2)

        if com1 is None or com2 is None:
            return None

        dist = np.sqrt((com1[0] - com2[0]) ** 2 + (com1[1] - com2[1]) ** 2)
        return float(dist)
