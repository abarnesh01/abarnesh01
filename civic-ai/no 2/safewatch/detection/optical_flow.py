"""
SafeWatch — Optical Flow Analyzer
Lucas-Kanade optical flow for motion analysis and crowd divergence detection.
"""

import threading
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
from loguru import logger


@dataclass
class FlowResult:
    """Result of optical flow analysis."""
    mean_magnitude: float
    max_magnitude: float
    flow_vectors: np.ndarray
    divergence_score: float
    motion_regions: list[tuple[int, int, int, int]]

    def __repr__(self) -> str:
        return (
            f"FlowResult(mean_mag={self.mean_magnitude:.2f}, "
            f"max_mag={self.max_magnitude:.2f}, "
            f"divergence={self.divergence_score:.2f})"
        )


class OpticalFlowAnalyzer:
    """Lucas-Kanade optical flow for motion and crowd divergence analysis."""

    def __init__(self, reset_interval: int = 30) -> None:
        self._reset_interval = reset_interval
        self._frame_count = 0
        self._prev_gray: Optional[np.ndarray] = None
        self._prev_points: Optional[np.ndarray] = None
        self._lock = threading.Lock()

        self._lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )

        self._feature_params = dict(
            maxCorners=200,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7,
        )

        logger.info(f"OpticalFlowAnalyzer initialized (reset_interval={reset_interval})")

    def __repr__(self) -> str:
        return f"OpticalFlowAnalyzer(reset_interval={self._reset_interval})"

    def _detect_features(self, gray: np.ndarray) -> Optional[np.ndarray]:
        """Detect good features to track."""
        points = cv2.goodFeaturesToTrack(gray, **self._feature_params)
        return points

    def analyze(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> FlowResult:
        """Analyze optical flow between two frames."""
        with self._lock:
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

            self._frame_count += 1

            if self._prev_points is None or self._frame_count % self._reset_interval == 0:
                self._prev_points = self._detect_features(prev_gray)
                self._prev_gray = prev_gray

            if self._prev_points is None or len(self._prev_points) < 5:
                self._prev_points = self._detect_features(prev_gray)
                if self._prev_points is None or len(self._prev_points) < 5:
                    self._prev_gray = curr_gray
                    return FlowResult(
                        mean_magnitude=0.0,
                        max_magnitude=0.0,
                        flow_vectors=np.array([]),
                        divergence_score=0.0,
                        motion_regions=[],
                    )

            next_points, status, _ = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray, self._prev_points, None, **self._lk_params
            )

            if next_points is None or status is None:
                self._prev_gray = curr_gray
                self._prev_points = self._detect_features(curr_gray)
                return FlowResult(
                    mean_magnitude=0.0,
                    max_magnitude=0.0,
                    flow_vectors=np.array([]),
                    divergence_score=0.0,
                    motion_regions=[],
                )

            good_mask = status.flatten() == 1
            good_prev = self._prev_points[good_mask]
            good_next = next_points[good_mask]

            if len(good_prev) == 0:
                self._prev_gray = curr_gray
                self._prev_points = self._detect_features(curr_gray)
                return FlowResult(
                    mean_magnitude=0.0,
                    max_magnitude=0.0,
                    flow_vectors=np.array([]),
                    divergence_score=0.0,
                    motion_regions=[],
                )

            flow_vectors = good_next - good_prev
            magnitudes = np.sqrt(flow_vectors[:, 0, 0] ** 2 + flow_vectors[:, 0, 1] ** 2)

            mean_mag = float(np.mean(magnitudes))
            max_mag = float(np.max(magnitudes))

            divergence_score = self._compute_divergence(good_prev, flow_vectors)

            motion_regions = self._find_motion_regions(
                good_next, magnitudes, curr_gray.shape
            )

            self._prev_gray = curr_gray
            self._prev_points = good_next.reshape(-1, 1, 2)

            return FlowResult(
                mean_magnitude=mean_mag,
                max_magnitude=max_mag,
                flow_vectors=flow_vectors,
                divergence_score=divergence_score,
                motion_regions=motion_regions,
            )

    def _compute_divergence(
        self, points: np.ndarray, flow_vectors: np.ndarray
    ) -> float:
        """Compute divergence score — high means people moving away from center."""
        if len(points) < 3:
            return 0.0

        center = np.mean(points.reshape(-1, 2), axis=0)
        divergence_values = []

        for i in range(len(points)):
            pt = points[i].flatten()
            fv = flow_vectors[i].flatten()

            radial = pt - center
            radial_norm = np.linalg.norm(radial)
            if radial_norm < 1e-5:
                continue

            radial_unit = radial / radial_norm
            flow_mag = np.linalg.norm(fv)
            if flow_mag < 1e-5:
                continue

            flow_unit = fv / flow_mag
            dot = np.dot(radial_unit, flow_unit)
            divergence_values.append(dot * flow_mag)

        if not divergence_values:
            return 0.0

        return float(np.mean(divergence_values))

    def _find_motion_regions(
        self,
        points: np.ndarray,
        magnitudes: np.ndarray,
        frame_shape: tuple,
    ) -> list[tuple[int, int, int, int]]:
        """Find bounding boxes of high-motion regions."""
        threshold = np.mean(magnitudes) + np.std(magnitudes) if len(magnitudes) > 1 else 5.0
        high_motion_mask = magnitudes > threshold
        high_pts = points[high_motion_mask]

        if len(high_pts) < 2:
            return []

        regions: list[tuple[int, int, int, int]] = []
        pts = high_pts.reshape(-1, 2).astype(int)

        x_min = int(np.min(pts[:, 0]))
        y_min = int(np.min(pts[:, 1]))
        x_max = int(np.max(pts[:, 0]))
        y_max = int(np.max(pts[:, 1]))

        pad = 20
        x_min = max(0, x_min - pad)
        y_min = max(0, y_min - pad)
        x_max = min(frame_shape[1] if len(frame_shape) > 1 else 640, x_max + pad)
        y_max = min(frame_shape[0], y_max + pad)

        regions.append((x_min, y_min, x_max, y_max))
        return regions

    def detect_sudden_motion(self, flow_result: FlowResult, threshold: float = 15.0) -> tuple[bool, float]:
        """Detect sudden large motion in the frame."""
        is_sudden = flow_result.max_magnitude > threshold
        return is_sudden, flow_result.max_magnitude

    def detect_crowd_divergence(
        self, flow_result: FlowResult, threshold: float = 8.0
    ) -> tuple[bool, float]:
        """Detect crowd divergence (people running away from center = panic)."""
        is_divergent = flow_result.divergence_score > threshold
        return is_divergent, flow_result.divergence_score

    def reset(self) -> None:
        """Reset tracking state."""
        with self._lock:
            self._prev_gray = None
            self._prev_points = None
            self._frame_count = 0
