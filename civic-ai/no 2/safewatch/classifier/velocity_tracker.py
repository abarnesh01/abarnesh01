import time
import numpy as np
from typing import Dict, List, Tuple
from collections import deque
from loguru import logger

class VelocityTracker:
    """Tracks movement velocity and acceleration of detected entities."""

    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.track_history: Dict[int, deque] = {} # track_id -> deque of (timestamp, position)

    def update(self, track_id: int, position: Tuple[int, int]) -> Dict[str, float]:
        """Updates position and calculates current velocity and acceleration."""
        now = time.time()
        
        if track_id not in self.track_history:
            self.track_history[track_id] = deque(maxlen=self.history_size)
            
        self.track_history[track_id].append((now, np.array(position)))
        
        if len(self.track_history[track_id]) < 2:
            return {"velocity": 0.0, "acceleration": 0.0}

        # Calculate velocity between last two points
        t2, p2 = self.track_history[track_id][-1]
        t1, p1 = self.track_history[track_id][-2]
        
        dt = t2 - t1
        if dt <= 0:
            return {"velocity": 0.0, "acceleration": 0.0}
            
        velocity_vec = (p2 - p1) / dt
        velocity_mag = np.linalg.norm(velocity_vec)

        # Calculate acceleration if we have 3 points
        acceleration = 0.0
        if len(self.track_history[track_id]) >= 3:
            t0, p0 = self.track_history[track_id][-3]
            dt_prev = t1 - t0
            if dt_prev > 0:
                v_prev = (p1 - p0) / dt_prev
                acceleration = np.linalg.norm(velocity_vec - v_prev) / dt

        return {
            "velocity": float(velocity_mag),
            "acceleration": float(acceleration)
        }

    def cleanup(self, active_ids: List[int]):
        """Removes history for IDs that are no longer active."""
        dead_ids = [tid for tid in self.track_history if tid not in active_ids]
        for tid in dead_ids:
            del self.track_history[tid]

    def get_avg_velocity(self, track_id: int) -> float:
        """Calculates average velocity over the tracked history."""
        if track_id not in self.track_history or len(self.track_history[track_id]) < 2:
            return 0.0
            
        history = list(self.track_history[track_id])
        total_dist = 0.0
        for i in range(1, len(history)):
            total_dist += np.linalg.norm(history[i][1] - history[i-1][1])
            
        total_time = history[-1][0] - history[0][0]
        return total_dist / total_time if total_time > 0 else 0.0
