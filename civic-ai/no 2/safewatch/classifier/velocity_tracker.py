import time
import numpy as np
from typing import Dict, List, Any, Optional
from collections import deque

class VelocityTracker:
    """
    Tracks the velocity and acceleration of detected persons over time.
    Maintains a rolling history for each track ID.
    """
    def __init__(self, history_size: int = 15):
        self.history_size = history_size
        # {track_id: deque([(timestamp, x, y), ...])}
        self.trajectories: Dict[int, deque] = {}

    def update(self, detections: List[Dict[str, Any]]):
        """Updates trajectories with new detection coordinates."""
        current_time = time.time()
        active_ids = set()
        
        for det in detections:
            track_id = det['id']
            if track_id == -1: continue
            
            active_ids.add(track_id)
            x1, y1, x2, y2 = det['bbox']
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            if track_id not in self.trajectories:
                self.trajectories[track_id] = deque(maxlen=self.history_size)
            
            self.trajectories[track_id].append((current_time, center[0], center[1]))

        # Cleanup lost tracks
        lost_ids = set(self.trajectories.keys()) - active_ids
        # We might want to keep history for a bit, but for velocity we only need active
        for lid in lost_ids:
            if len(self.trajectories[lid]) > 0:
                # Expire after some time if needed, for now just keep it limited
                pass

    def get_velocity(self, track_id: int) -> float:
        """Returns the average velocity (pixels/sec) of a person."""
        if track_id not in self.trajectories or len(self.trajectories[track_id]) < 2:
            return 0.0
            
        traj = self.trajectories[track_id]
        t1, x1, y1 = traj[0]
        t2, x2, y2 = traj[-1]
        
        dt = t2 - t1
        if dt <= 0: return 0.0
        
        dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist / dt

    def get_acceleration(self, track_id: int) -> float:
        """Returns the change in velocity over the history window."""
        if track_id not in self.trajectories or len(self.trajectories[track_id]) < 3:
            return 0.0
            
        traj = list(self.trajectories[track_id])
        # Split history in two to compare velocities
        mid = len(traj) // 2
        
        v1 = self._calc_v(traj[:mid+1])
        v2 = self._calc_v(traj[mid:])
        
        dt = traj[-1][0] - traj[0][0]
        if dt <= 0: return 0.0
        
        return (v2 - v1) / dt

    def _calc_v(self, points: List[Tuple[float, float, float]]) -> float:
        if len(points) < 2: return 0.0
        t1, x1, y1 = points[0]
        t2, x2, y2 = points[-1]
        dt = t2 - t1
        if dt <= 0: return 0.0
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2) / dt

    def is_sudden_stop(self, track_id: int) -> bool:
        """Detects sudden impact or collapse based on deceleration."""
        acc = self.get_acceleration(track_id)
        # Large negative acceleration
        return acc < -500 # Threshold heuristic
