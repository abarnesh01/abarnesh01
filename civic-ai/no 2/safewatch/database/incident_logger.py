import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from .db_manager import DatabaseManager

class IncidentLogger:
    """High-level logger for recording threat incidents and system events."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def log_incident(self, 
                     camera_id: str, 
                     threat_type: str, 
                     severity: str, 
                     confidence: float, 
                     snapshot_path: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> int:
        """Logs a detected threat incident to the database."""
        query = """
            INSERT INTO incidents (camera_id, threat_type, severity, confidence, snapshot_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        meta_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor = self.db.execute(query, (camera_id, threat_type, severity, confidence, snapshot_path, meta_json))
            incident_id = cursor.lastrowid
            logger.info(f"Incident logged: {threat_type} ({severity}) on {camera_id} - ID: {incident_id}")
            return incident_id
        except Exception as e:
            logger.error(f"Failed to log incident: {e}")
            return -1

    def log_camera_health(self, camera_id: str, status: str, fps: float, latency: float):
        """Logs camera performance metrics."""
        query = """
            INSERT INTO camera_health (camera_id, status, fps, latency)
            VALUES (?, ?, ?, ?)
        """
        try:
            self.db.execute(query, (camera_id, status, fps, latency))
        except Exception as e:
            logger.error(f"Failed to log camera health: {e}")

    def get_recent_incidents(self, limit: int = 50):
        """Retrieves most recent incidents."""
        query = "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?"
        return self.db.fetch_all(query, (limit,))

    def update_incident_status(self, incident_id: int, status: str):
        """Updates the status of an incident (e.g., ACKNOWLEDGED, RESOLVED)."""
        query = "UPDATE incidents SET status = ? WHERE id = ?"
        try:
            self.db.execute(query, (status, incident_id))
            logger.info(f"Incident {incident_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Failed to update incident status: {e}")
