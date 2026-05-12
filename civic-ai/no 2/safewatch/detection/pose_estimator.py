"""
SafeWatch — Pose Estimator
MediaPipe-based pose estimation with skeleton drawing and joint utilities.
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    logger.warning("MediaPipe not available — pose estimation disabled")

from detection.person_detector import Person


KEYPOINT_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]

SKELETON_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26),
    (25, 27), (26, 28), (0, 11), (0, 12),
]


@dataclass
class Landmark:
    """A single pose landmark."""
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class PoseResult:
    """Pose estimation result for a single person."""
    person_id: int
    landmarks: list[Landmark]
    keypoints: dict[str, Landmark]
    bbox: tuple[int, int, int, int]
    confidence: float

    def __repr__(self) -> str:
        n_visible = sum(1 for lm in self.landmarks if lm.visibility > 0.5)
        return f"PoseResult(person={self.person_id}, visible_landmarks={n_visible}/{len(self.landmarks)})"

    def get_landmark(self, name: str) -> Optional[Landmark]:
        """Get a named landmark, returns None if not found or low visibility."""
        lm = self.keypoints.get(name)
        if lm is not None and lm.visibility > 0.3:
            return lm
        return None


class PoseEstimator:
    """MediaPipe-based pose estimator for detected persons."""

    def __init__(
        self,
        model_complexity: int = 0,
        min_confidence: float = 0.5,
    ) -> None:
        self._model_complexity = model_complexity
        self._min_confidence = min_confidence
        self._lock = threading.Lock()
        self._pose = None

        if MP_AVAILABLE:
            self._mp_pose = mp.solutions.pose
            self._mp_drawing = mp.solutions.drawing_utils
            self._pose = self._mp_pose.Pose(
                static_image_mode=False,
                model_complexity=model_complexity,
                min_detection_confidence=min_confidence,
                min_tracking_confidence=min_confidence,
            )
            logger.info(f"PoseEstimator initialized (complexity={model_complexity})")
        else:
            logger.warning("PoseEstimator: MediaPipe unavailable, estimation disabled")

    def __repr__(self) -> str:
        status = "active" if self._pose else "disabled"
        return f"PoseEstimator(complexity={self._model_complexity}, status={status})"

    def estimate(self, frame: np.ndarray, persons: list[Person]) -> list[PoseResult]:
        """Estimate poses for detected persons. Crops each person's bbox and runs pose."""
        if self._pose is None:
            return []

        results: list[PoseResult] = []
        h, w = frame.shape[:2]

        for person in persons:
            x1, y1, x2, y2 = person.bbox
            pad_x = int((x2 - x1) * 0.1)
            pad_y = int((y2 - y1) * 0.1)
            cx1 = max(0, x1 - pad_x)
            cy1 = max(0, y1 - pad_y)
            cx2 = min(w, x2 + pad_x)
            cy2 = min(h, y2 + pad_y)

            crop = frame[cy1:cy2, cx1:cx2]
            if crop.size == 0:
                continue

            try:
                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                with self._lock:
                    pose_result = self._pose.process(crop_rgb)

                if pose_result.pose_landmarks is None:
                    continue

                crop_h, crop_w = crop.shape[:2]
                landmarks: list[Landmark] = []
                keypoints: dict[str, Landmark] = {}

                for idx, lm in enumerate(pose_result.pose_landmarks.landmark):
                    abs_x = (lm.x * crop_w + cx1) / w
                    abs_y = (lm.y * crop_h + cy1) / h
                    landmark = Landmark(
                        x=abs_x,
                        y=abs_y,
                        z=lm.z,
                        visibility=lm.visibility,
                    )
                    landmarks.append(landmark)
                    if idx < len(KEYPOINT_NAMES):
                        keypoints[KEYPOINT_NAMES[idx]] = landmark

                avg_vis = np.mean([lm.visibility for lm in landmarks])
                if avg_vis < self._min_confidence * 0.5:
                    continue

                pose_res = PoseResult(
                    person_id=person.id,
                    landmarks=landmarks,
                    keypoints=keypoints,
                    bbox=person.bbox,
                    confidence=float(avg_vis),
                )
                results.append(pose_res)

            except Exception as e:
                logger.debug(f"Pose estimation failed for person {person.id}: {e}")
                continue

        return results

    def draw_skeleton(self, frame: np.ndarray, pose_results: list[PoseResult]) -> np.ndarray:
        """Draw skeletons on the frame for all pose results."""
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        for pose in pose_results:
            points: list[Optional[tuple[int, int]]] = []
            for lm in pose.landmarks:
                if lm.visibility > 0.3:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    points.append((px, py))
                    cv2.circle(annotated, (px, py), 3, (0, 255, 255), -1)
                else:
                    points.append(None)

            for start_idx, end_idx in SKELETON_CONNECTIONS:
                if start_idx < len(points) and end_idx < len(points):
                    p1 = points[start_idx]
                    p2 = points[end_idx]
                    if p1 is not None and p2 is not None:
                        cv2.line(annotated, p1, p2, (0, 255, 255), 2)

        return annotated

    @staticmethod
    def get_body_angle(
        pose: PoseResult,
        joint1_name: str,
        joint2_name: str,
        joint3_name: str,
    ) -> Optional[float]:
        """Calculate angle at joint2 between joint1-joint2-joint3 in degrees."""
        j1 = pose.get_landmark(joint1_name)
        j2 = pose.get_landmark(joint2_name)
        j3 = pose.get_landmark(joint3_name)

        if any(j is None for j in [j1, j2, j3]):
            return None

        v1 = np.array([j1.x - j2.x, j1.y - j2.y])
        v2 = np.array([j3.x - j2.x, j3.y - j2.y])

        dot = np.dot(v1, v2)
        mag1 = np.linalg.norm(v1)
        mag2 = np.linalg.norm(v2)

        if mag1 == 0 or mag2 == 0:
            return None

        cos_angle = np.clip(dot / (mag1 * mag2), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        return float(angle)

    @staticmethod
    def get_joint_velocity(
        pose: PoseResult,
        joint_name: str,
        previous_pose: Optional[PoseResult],
        dt: float = 1.0 / 15.0,
    ) -> Optional[float]:
        """Calculate velocity of a joint between two consecutive poses (pixels/sec)."""
        if previous_pose is None:
            return None

        curr = pose.get_landmark(joint_name)
        prev = previous_pose.get_landmark(joint_name)

        if curr is None or prev is None:
            return None

        dx = curr.x - prev.x
        dy = curr.y - prev.y
        dist = np.sqrt(dx ** 2 + dy ** 2)

        if dt <= 0:
            return None
        velocity = dist / dt
        return float(velocity)

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._pose is not None:
            self._pose.close()
            self._pose = None
            logger.info("PoseEstimator closed")
