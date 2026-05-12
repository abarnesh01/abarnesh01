"""
SafeWatch — Zone Manager
Polygon-based restricted zone management for trespass detection.
"""

import json
import threading
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger

from detection.person_detector import Person


class ZoneManager:
    """Manages named polygon zones for restricted area detection."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        self._zones: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._config_path = Path(config_path)
        self._zones_file = Path("logs/zones.json")
        self._load_zones()
        logger.info(f"ZoneManager initialized with {len(self._zones)} zones")

    def __repr__(self) -> str:
        return f"ZoneManager(zones={list(self._zones.keys())})"

    def _load_zones(self) -> None:
        """Load zones from zones.json if it exists."""
        if self._zones_file.exists():
            try:
                with open(self._zones_file, "r") as f:
                    data = json.load(f)
                for name, zone_data in data.items():
                    self._zones[name] = {
                        "polygon": np.array(zone_data["polygon"], dtype=np.int32),
                        "zone_type": zone_data.get("zone_type", "restricted"),
                    }
                logger.info(f"Loaded {len(self._zones)} zones from {self._zones_file}")
            except Exception as e:
                logger.warning(f"Failed to load zones: {e}")

    def _save_zones(self) -> None:
        """Save zones to zones.json."""
        try:
            self._zones_file.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            for name, zone_data in self._zones.items():
                data[name] = {
                    "polygon": zone_data["polygon"].tolist(),
                    "zone_type": zone_data["zone_type"],
                }
            with open(self._zones_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Zones saved to {self._zones_file}")
        except Exception as e:
            logger.error(f"Failed to save zones: {e}")

    def add_zone(
        self,
        name: str,
        polygon_points: list[tuple[int, int]],
        zone_type: str = "restricted",
    ) -> None:
        """Add a named polygon zone."""
        with self._lock:
            self._zones[name] = {
                "polygon": np.array(polygon_points, dtype=np.int32),
                "zone_type": zone_type,
            }
            self._save_zones()
        logger.info(f"Zone added: {name} ({zone_type}), points={len(polygon_points)}")

    def remove_zone(self, name: str) -> bool:
        """Remove a named zone."""
        with self._lock:
            if name in self._zones:
                del self._zones[name]
                self._save_zones()
                logger.info(f"Zone removed: {name}")
                return True
        return False

    def is_in_zone(self, point: tuple[int, int], zone_name: str) -> bool:
        """Check if a point is inside a named zone polygon."""
        with self._lock:
            zone = self._zones.get(zone_name)
        if zone is None:
            return False

        polygon = zone["polygon"]
        result = cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False)
        return result >= 0

    def get_violations(
        self, persons: list[Person], zone_name: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get all persons inside restricted zones. Optionally filter by zone_name."""
        violations: list[dict[str, Any]] = []

        with self._lock:
            zones_to_check = {}
            if zone_name and zone_name in self._zones:
                zones_to_check[zone_name] = self._zones[zone_name]
            else:
                zones_to_check = dict(self._zones)

        for person in persons:
            for z_name, zone_data in zones_to_check.items():
                polygon = zone_data["polygon"]
                center = (float(person.center[0]), float(person.center[1]))
                result = cv2.pointPolygonTest(polygon, center, False)
                if result >= 0:
                    violations.append({
                        "person_id": person.id,
                        "person_center": person.center,
                        "zone_name": z_name,
                        "zone_type": zone_data["zone_type"],
                    })

        return violations

    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """Draw all zone polygons on the frame with labels."""
        annotated = frame.copy()
        overlay = annotated.copy()

        with self._lock:
            zones = dict(self._zones)

        color_map = {
            "restricted": (0, 0, 255),
            "critical": (128, 0, 128),
            "entrance": (255, 165, 0),
            "outdoor": (0, 200, 0),
        }

        for name, zone_data in zones.items():
            polygon = zone_data["polygon"]
            zone_type = zone_data["zone_type"]
            color = color_map.get(zone_type, (0, 0, 255))

            cv2.fillPoly(overlay, [polygon], color)
            cv2.polylines(annotated, [polygon], isClosed=True, color=color, thickness=2)

            centroid = np.mean(polygon, axis=0).astype(int)
            label = f"{name} ({zone_type})"
            cv2.putText(
                annotated,
                label,
                (centroid[0] - 30, centroid[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        alpha = 0.25
        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)
        return annotated

    def get_zone_names(self) -> list[str]:
        """Get list of all zone names."""
        with self._lock:
            return list(self._zones.keys())

    def get_zone_info(self, name: str) -> Optional[dict[str, Any]]:
        """Get info about a specific zone."""
        with self._lock:
            zone = self._zones.get(name)
        if zone is None:
            return None
        return {
            "name": name,
            "zone_type": zone["zone_type"],
            "polygon": zone["polygon"].tolist(),
            "num_points": len(zone["polygon"]),
        }
