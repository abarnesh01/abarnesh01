import cv2
import numpy as np
from loguru import logger
from typing import List, Dict, Tuple

class ZoneManager:
    """Manages virtual restricted zones and detects trespassing."""

    def __init__(self):
        self.zones: Dict[str, List[Tuple[int, int]]] = {} # name -> polygon points
        logger.info("Zone Manager initialized.")

    def add_zone(self, name: str, points: List[Tuple[int, int]]):
        """Adds a polygonal restricted zone."""
        self.zones[name] = points
        logger.info(f"Zone '{name}' added with {len(points)} points.")

    def remove_zone(self, name: str):
        if name in self.zones:
            del self.zones[name]
            logger.info(f"Zone '{name}' removed.")

    def is_in_zone(self, point: Tuple[int, int], zone_name: str) -> bool:
        """Checks if a point is inside a specific zone."""
        if zone_name not in self.zones:
            return False
        
        polygon = np.array(self.zones[zone_name], np.int32)
        result = cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False)
        return result >= 0

    def check_trespass(self, detections: List[Dict]) -> List[Dict]:
        """Checks if any detected person is within any restricted zone."""
        trespassers = []
        for det in detections:
            bbox = det["bbox"]
            # Bottom center of bounding box as the ground point
            feet_point = ((bbox[0] + bbox[2]) // 2, bbox[3])
            
            for zone_name, points in self.zones.items():
                if self.is_in_zone(feet_point, zone_name):
                    trespassers.append({
                        "id": det["id"],
                        "zone": zone_name,
                        "point": feet_point
                    })
        return trespassers

    def draw_zones(self, frame: cv2.Mat):
        """Renders zones on the frame."""
        for name, points in self.zones.items():
            poly = np.array(points, np.int32)
            cv2.polylines(frame, [poly], True, (0, 0, 255), 2)
            cv2.putText(frame, f"Restricted: {name}", (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        return frame
