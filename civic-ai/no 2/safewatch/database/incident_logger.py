"""
SafeWatch — Incident Logger
High-level wrapper around DatabaseManager for threat event logging.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from database.db_manager import DatabaseManager


class IncidentLogger:
    """High-level incident logging and statistics interface."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager
        logger.info("IncidentLogger initialized")

    def __repr__(self) -> str:
        return f"IncidentLogger(db={self._db!r})"

    def log_threat(
        self,
        threat_event: dict[str, Any],
        camera_id: str,
        snapshot_path: str = "",
        recording_path: str = "",
    ) -> int:
        """Log a threat event to the database. Returns incident ID."""
        incident_data = {
            "camera_id": camera_id,
            "timestamp": threat_event.get("timestamp", datetime.now().isoformat()),
            "threat_type": threat_event.get("threat_type", "unknown"),
            "confidence": threat_event.get("confidence", 0.0),
            "severity": threat_event.get("severity", "LOW"),
            "persons_involved": threat_event.get("persons_involved", 0),
            "description": threat_event.get("description", ""),
            "snapshot_path": snapshot_path,
            "recording_path": recording_path,
            "alert_sent": threat_event.get("alert_sent", 0),
            "acknowledged": 0,
        }
        incident_id = self._db.log_incident(incident_data)
        if incident_id > 0:
            logger.info(
                f"Threat logged: ID={incident_id}, type={incident_data['threat_type']}, "
                f"severity={incident_data['severity']}, camera={camera_id}"
            )
        return incident_id

    def get_threat_stats(self, last_hours: int = 24) -> dict[str, Any]:
        """Get threat statistics for the last N hours."""
        start_time = (datetime.now() - timedelta(hours=last_hours)).isoformat()
        incidents = self._db.get_incidents(start_date=start_time, limit=10000)

        stats: dict[str, Any] = {
            "period_hours": last_hours,
            "total_incidents": len(incidents),
            "by_type": {},
            "by_severity": {},
            "by_camera": {},
            "avg_confidence": 0.0,
        }

        if not incidents:
            return stats

        type_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        camera_counts: dict[str, int] = {}
        total_confidence = 0.0

        for inc in incidents:
            t_type = inc.get("threat_type", "unknown")
            type_counts[t_type] = type_counts.get(t_type, 0) + 1

            sev = inc.get("severity", "LOW")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

            cam = inc.get("camera_id", "UNKNOWN")
            camera_counts[cam] = camera_counts.get(cam, 0) + 1

            total_confidence += inc.get("confidence", 0.0)

        stats["by_type"] = type_counts
        stats["by_severity"] = severity_counts
        stats["by_camera"] = camera_counts
        stats["avg_confidence"] = total_confidence / len(incidents)

        return stats

    def get_timeline(self, camera_id: str, date: Optional[str] = None) -> list[dict[str, Any]]:
        """Get an ordered list of incidents for a camera on a given date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        start_date = f"{date}T00:00:00"
        end_date = f"{date}T23:59:59"

        incidents = self._db.get_incidents(
            camera_id=camera_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )
        return sorted(incidents, key=lambda x: x.get("timestamp", ""))

    def export_csv(self, start_date: str, end_date: str, output_path: str) -> str:
        """Export incidents to CSV file. Returns the output file path."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        incidents = self._db.get_incidents(
            start_date=start_date,
            end_date=end_date,
            limit=100000,
        )

        fieldnames = [
            "id", "camera_id", "timestamp", "threat_type", "confidence",
            "severity", "persons_involved", "description", "snapshot_path",
            "recording_path", "alert_sent", "acknowledged", "created_at",
        ]

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for incident in incidents:
                writer.writerow(incident)

        logger.info(f"Exported {len(incidents)} incidents to {output_path}")
        return str(output)

    def get_unacknowledged(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get unacknowledged incidents."""
        all_incidents = self._db.get_incidents(limit=limit)
        return [inc for inc in all_incidents if not inc.get("acknowledged", 0)]

    def acknowledge(self, incident_id: int) -> bool:
        """Acknowledge an incident."""
        result = self._db.mark_incident_acknowledged(incident_id)
        if result:
            logger.info(f"Incident {incident_id} acknowledged")
        return result
