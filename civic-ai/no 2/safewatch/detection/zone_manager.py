import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from loguru import logger

class ZoneManager:
    """
    Manages exclusion/inclusion zones for monitoring.
    Used for trespassing detection and masking out non-interest areas.
    """
    def __init__(self):
        self.zones: Dict[str, List[Tuple[int, int]]] = {} # Name -> List of points

    def add_zone(self, name: str, points: List[Tuple[int, int]]):
        """Adds a polygonal zone."""
        self.zones[name] = points
        logger.info(f"Zone '{name}' added with {len(points)} points.")

    def is_in_zone(self, point: Tuple[int, int], zone_name: str) -> bool:
        """Checks if a point (x, y) is inside a specific zone."""
        if zone_name not in self.zones:
            return False
            
        pts = np.array(self.zones[zone_name], dtype=np.int32)
        result = cv2.pointPolygonTest(pts, point, False)
        return result >= 0

    def check_detections(self, detections: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """
        Checks which zones each detected person is currently in.
        Returns mapping {track_id: [zone_name1, zone_name2]}
        """
        results = {}
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            # Use bottom center as the reference point for zone checking (feet position)
            feet_pos = ((x1 + x2) // 2, y2)
            
            active_zones = []
            for name in self.zones:
                if self.is_in_zone(feet_pos, name):
                    active_zones.append(name)
            
            results[det['id']] = active_zones
        return results

    def draw_zones(self, frame: np.ndarray):
        """Visualizes zones on the frame."""
        overlay = frame.copy()
        for name, points in self.zones.items():
            pts = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
            cv2.fillPoly(overlay, [pts], (0, 255, 255))
            
            # Label
            x, y = points[0]
            cv2.putText(frame, name, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
        # Semi-transparent overlay
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        return frame
