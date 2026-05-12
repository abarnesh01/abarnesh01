"""
SafeWatch — Velocity Tracker
Tracks position history and computes velocities/accelerations for person joints.
"""

import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import numpy as np
from loguru import logger

from detection.pose_estimator import PoseResult


@dataclass
class TrackEntry:
    """A single tracking entry for a person at a timestamp."""
    timestamp: float
    positions: dict[str, tuple[float, float]]  # joint_name -> (x, y)


class VelocityTracker:
    """Tracks per-person joint positions over time for velocity/acceleration computation."""

    def __init__(self, max_history: int = 60, stale_timeout: float = 5.0) -> None:
        self._max_history = max_history
        self._stale_timeout = stale_timeout
        self._history: dict[int, list[TrackEntry]] = defaultdict(list)
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        logger.info(f"VelocityTracker initialized (history={max_history}, stale={stale_timeout}s)")

    def __repr__(self) -> str:
        with self._lock:
            n = len(self._history)
        return f"VelocityTracker(tracking={n} persons)"

    def update(self, person_id: int, pose_result: PoseResult, timestamp: float) -> None:
        """Update position history for a person."""
        positions: dict[str, tuple[float, float]] = {}
        for name, lm in pose_result.keypoints.items():
            if lm.visibility > 0.3:
                positions[name] = (lm.x, lm.y)

        entry = TrackEntry(timestamp=timestamp, positions=positions)

        with self._lock:
            history = self._history[person_id]
            history.append(entry)
            if len(history) > self._max_history:
                self._history[person_id] = history[-self._max_history:]

        if time.time() - self._last_cleanup > 10.0:
            self._cleanup_stale()

    def get_velocity(self, person_id: int, joint_name: str) -> float:
        """Get velocity of a joint in normalized units per second."""
        with self._lock:
            history = self._history.get(person_id, [])

        if len(history) < 2:
            return 0.0

        curr = history[-1]
        prev = history[-2]

        curr_pos = curr.positions.get(joint_name)
        prev_pos = prev.positions.get(joint_name)

        if curr_pos is None or prev_pos is None:
            return 0.0

        dt = curr.timestamp - prev.timestamp
        if dt <= 0:
            return 0.0

        dx = curr_pos[0] - prev_pos[0]
        dy = curr_pos[1] - prev_pos[1]
        dist = np.sqrt(dx ** 2 + dy ** 2)

        return float(dist / dt)

    def get_acceleration(self, person_id: int, joint_name: str) -> float:
        """Get acceleration of a joint in normalized units per second²."""
        with self._lock:
            history = self._history.get(person_id, [])

        if len(history) < 3:
            return 0.0

        entries = history[-3:]

        velocities = []
        for i in range(1, len(entries)):
            curr = entries[i]
            prev = entries[i - 1]
            curr_pos = curr.positions.get(joint_name)
            prev_pos = prev.positions.get(joint_name)

            if curr_pos is None or prev_pos is None:
                return 0.0

            dt = curr.timestamp - prev.timestamp
            if dt <= 0:
                return 0.0

            dx = curr_pos[0] - prev_pos[0]
            dy = curr_pos[1] - prev_pos[1]
            vel = np.sqrt(dx ** 2 + dy ** 2) / dt
            velocities.append((vel, curr.timestamp))

        if len(velocities) < 2:
            return 0.0

        dv = velocities[-1][0] - velocities[-2][0]
        dt = velocities[-1][1] - velocities[-2][1]

        if dt <= 0:
            return 0.0

        return float(dv / dt)

    def get_trajectory(self, person_id: int, n_frames: int = 10) -> list[tuple[float, float]]:
        """Get recent trajectory (center of mass positions) for a person."""
        with self._lock:
            history = self._history.get(person_id, [])

        positions = []
        for entry in history[-n_frames:]:
            hip_positions = []
            for joint in ["left_hip", "right_hip"]:
                pos = entry.positions.get(joint)
                if pos is not None:
                    hip_positions.append(pos)

            if hip_positions:
                avg_x = np.mean([p[0] for p in hip_positions])
                avg_y = np.mean([p[1] for p in hip_positions])
                positions.append((float(avg_x), float(avg_y)))

        return positions

    def get_relative_velocity(self, person_id_1: int, person_id_2: int) -> float:
        """Get relative velocity (closing/opening speed) between two persons."""
        with self._lock:
            h1 = self._history.get(person_id_1, [])
            h2 = self._history.get(person_id_2, [])

        if len(h1) < 2 or len(h2) < 2:
            return 0.0

        def _get_center(entry: TrackEntry) -> Optional[tuple[float, float]]:
            positions = []
            for joint in ["left_hip", "right_hip", "left_shoulder", "right_shoulder"]:
                pos = entry.positions.get(joint)
                if pos is not None:
                    positions.append(pos)
            if not positions:
                return None
            return (
                float(np.mean([p[0] for p in positions])),
                float(np.mean([p[1] for p in positions])),
            )

        c1_curr = _get_center(h1[-1])
        c1_prev = _get_center(h1[-2])
        c2_curr = _get_center(h2[-1])
        c2_prev = _get_center(h2[-2])

        if any(c is None for c in [c1_curr, c1_prev, c2_curr, c2_prev]):
            return 0.0

        dist_curr = np.sqrt(
            (c1_curr[0] - c2_curr[0]) ** 2 + (c1_curr[1] - c2_curr[1]) ** 2
        )
        dist_prev = np.sqrt(
            (c1_prev[0] - c2_prev[0]) ** 2 + (c1_prev[1] - c2_prev[1]) ** 2
        )

        dt1 = h1[-1].timestamp - h1[-2].timestamp
        dt2 = h2[-1].timestamp - h2[-2].timestamp
        dt = max(dt1, dt2)

        if dt <= 0:
            return 0.0

        return float((dist_prev - dist_curr) / dt)

    def get_average_velocity(self, person_id: int, n_frames: int = 5) -> float:
        """Get average velocity across all tracked joints over last N frames."""
        with self._lock:
            history = self._history.get(person_id, [])

        if len(history) < 2:
            return 0.0

        entries = history[-min(n_frames + 1, len(history)):]
        velocities = []

        for i in range(1, len(entries)):
            curr = entries[i]
            prev = entries[i - 1]
            dt = curr.timestamp - prev.timestamp
            if dt <= 0:
                continue

            for joint_name in curr.positions:
                curr_pos = curr.positions.get(joint_name)
                prev_pos = prev.positions.get(joint_name)
                if curr_pos and prev_pos:
                    dx = curr_pos[0] - prev_pos[0]
                    dy = curr_pos[1] - prev_pos[1]
                    vel = np.sqrt(dx ** 2 + dy ** 2) / dt
                    velocities.append(vel)

        if not velocities:
            return 0.0

        return float(np.mean(velocities))

    def get_joint_position(self, person_id: int, joint_name: str) -> Optional[tuple[float, float]]:
        """Get the latest position of a joint for a person."""
        with self._lock:
            history = self._history.get(person_id, [])
        if not history:
            return None
        return history[-1].positions.get(joint_name)

    def _cleanup_stale(self) -> None:
        """Remove entries for persons not seen recently."""
        now = time.time()
        self._last_cleanup = now

        with self._lock:
            stale_ids = []
            for pid, history in self._history.items():
                if history and (now - history[-1].timestamp) > self._stale_timeout:
                    stale_ids.append(pid)

            for pid in stale_ids:
                del self._history[pid]

            if stale_ids:
                logger.debug(f"Cleaned up {len(stale_ids)} stale person tracks")

    def get_tracked_ids(self) -> list[int]:
        """Get list of currently tracked person IDs."""
        with self._lock:
            return list(self._history.keys())
