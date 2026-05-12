"""
SafeWatch — Trespass Detector
Detects persons entering restricted polygon zones.
"""

import time
from collections import defaultdict
from typing import Any, Optional

from loguru import logger

from detection.person_detector import Person
from detection.zone_manager import ZoneManager


class TrespassDetector:
    """Detects trespass into restricted zones with dwell time tracking."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._confidence_threshold = config.get("confidence_threshold", 0.95)
        self._dwell_time_alert = 5.0  # seconds
        self._person_zone_entry: dict[tuple[int, str], float] = {}
        self._alerted_pairs: dict[tuple[int, str], float] = {}
        logger.info("TrespassDetector initialized")

    def __repr__(self) -> str:
        return f"TrespassDetector(threshold={self._confidence_threshold})"

    def detect(
        self,
        persons: list[Person],
        zone_manager: ZoneManager,
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Detect trespass events."""
        threats: list[dict[str, Any]] = []
        now = time.time()

        current_violations: set[tuple[int, str]] = set()

        for person in persons:
            violations = zone_manager.get_violations([person])
            for violation in violations:
                zone_name = violation["zone_name"]
                zone_type = violation["zone_type"]
                pair_key = (person.id, zone_name)
                current_violations.add(pair_key)

                if pair_key not in self._person_zone_entry:
                    self._person_zone_entry[pair_key] = now

                dwell_time = now - self._person_zone_entry[pair_key]

                # Cooldown: don't re-alert same person in same zone within 30s
                last_alert = self._alerted_pairs.get(pair_key, 0)
                if now - last_alert < 30:
                    continue

                if zone_type == "critical":
                    # Alert immediately for critical zones
                    self._alerted_pairs[pair_key] = now
                    threats.append({
                        "threat_type": "trespass",
                        "confidence": self._confidence_threshold,
                        "persons_involved": 1,
                        "person_ids": [person.id],
                        "location_bbox": (
                            person.center[0] - person.width // 2,
                            person.center[1] - person.height // 2,
                            person.center[0] + person.width // 2,
                            person.center[1] + person.height // 2,
                        ),
                        "description": (
                            f"Person {person.id} entered CRITICAL restricted zone '{zone_name}'. "
                            f"Immediate response required."
                        ),
                        "severity": "CRITICAL",
                    })
                elif dwell_time >= self._dwell_time_alert:
                    # Alert after dwell time for other zones
                    severity = "HIGH" if dwell_time > 10 else "MEDIUM"
                    self._alerted_pairs[pair_key] = now
                    threats.append({
                        "threat_type": "trespass",
                        "confidence": self._confidence_threshold,
                        "persons_involved": 1,
                        "person_ids": [person.id],
                        "location_bbox": (
                            person.center[0] - person.width // 2,
                            person.center[1] - person.height // 2,
                            person.center[0] + person.width // 2,
                            person.center[1] + person.height // 2,
                        ),
                        "description": (
                            f"Person {person.id} in restricted zone '{zone_name}' "
                            f"for {dwell_time:.1f}s. Zone type: {zone_type}."
                        ),
                        "severity": severity,
                    })

        # Clean up entries for persons who left zones
        stale_keys = [k for k in self._person_zone_entry if k not in current_violations]
        for key in stale_keys:
            del self._person_zone_entry[key]

        return threats
