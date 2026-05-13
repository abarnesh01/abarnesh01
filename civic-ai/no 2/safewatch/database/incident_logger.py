import json
from datetime import datetime
from loguru import logger
from typing import Optional, Dict, Any
from database.db_manager import db

class IncidentLogger:
    """
    Handles logging of security incidents and camera health to the database.
    """
    
    @staticmethod
    def log_incident(
        camera_id: int,
        camera_name: str,
        threat_type: str,
        severity: str,
        confidence: float,
        snapshot_path: Optional[str] = None,
        video_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Logs a detected threat incident to the database.
        Returns the ID of the inserted record.
        """
        meta_json = json.dumps(metadata) if metadata else "{}"
        
        query = """
            INSERT INTO incidents 
            (camera_id, camera_name, threat_type, severity, confidence, snapshot_path, video_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (camera_id, camera_name, threat_type, severity, confidence, snapshot_path, video_path, meta_json)
        
        if db.execute(query, params):
            res = db.fetch_one("SELECT last_insert_rowid() as id")
            incident_id = res['id'] if res else -1
            logger.info(f"Incident Logged [{incident_id}]: {threat_type} ({severity}) at {camera_name}")
            return incident_id
        return -1

    @staticmethod
    def update_camera_health(
        camera_id: int,
        camera_name: str,
        status: str,
        error_msg: Optional[str] = None
    ):
        """
        Updates the health status of a camera stream.
        """
        query = """
            INSERT INTO camera_health (camera_id, camera_name, status, last_seen, error_msg)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(camera_id) DO UPDATE SET
                status = excluded.status,
                last_seen = CURRENT_TIMESTAMP,
                error_msg = excluded.error_msg
        """
        params = (camera_id, camera_name, status, error_msg)
        db.execute(query, params)

    @staticmethod
    def get_recent_incidents(limit: int = 50):
        """Retrieves most recent incidents for the dashboard."""
        return db.fetch_all("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))

    @staticmethod
    def export_to_csv(filepath: str):
        """Exports all incidents to a CSV file."""
        import csv
        incidents = db.fetch_all("SELECT * FROM incidents")
        if not incidents:
            return False
            
        try:
            with open(filepath, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=incidents[0].keys())
                writer.writeheader()
                writer.writerows(incidents)
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return False
