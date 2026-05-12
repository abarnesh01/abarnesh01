"""
SafeWatch — Database Manager
SQLite database management for incident logging and system state.
"""

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from loguru import logger


class DatabaseManager:
    """Manages SQLite database for SafeWatch incident and system logging."""

    def __init__(self, db_path: str = "logs/safewatch.db") -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_database()
        logger.info(f"DatabaseManager initialized at {self._db_path}")

    def __repr__(self) -> str:
        return f"DatabaseManager(db_path='{self._db_path}')"

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection for the current thread."""
        conn = sqlite3.connect(str(self._db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_database(self) -> None:
        """Create all required tables if they don't exist."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        camera_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        threat_type TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        severity TEXT NOT NULL,
                        persons_involved INTEGER DEFAULT 0,
                        description TEXT,
                        snapshot_path TEXT,
                        recording_path TEXT,
                        alert_sent INTEGER DEFAULT 0,
                        acknowledged INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        camera_id TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS camera_status (
                        camera_id TEXT PRIMARY KEY,
                        last_seen DATETIME,
                        status TEXT DEFAULT 'offline',
                        fps REAL DEFAULT 0.0,
                        frames_processed INTEGER DEFAULT 0,
                        threats_today INTEGER DEFAULT 0
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_incidents_camera
                    ON incidents(camera_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_incidents_timestamp
                    ON incidents(timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_incidents_threat_type
                    ON incidents(threat_type)
                """)
                conn.commit()
                logger.debug("Database tables initialized successfully")
            except sqlite3.Error as e:
                logger.error(f"Database initialization error: {e}")
                raise
            finally:
                conn.close()

    def log_incident(self, incident_data: dict[str, Any]) -> int:
        """Log a threat incident to the database. Returns the incident ID."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO incidents (
                        camera_id, timestamp, threat_type, confidence,
                        severity, persons_involved, description,
                        snapshot_path, recording_path, alert_sent, acknowledged
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_data.get("camera_id", "UNKNOWN"),
                    incident_data.get("timestamp", datetime.now().isoformat()),
                    incident_data.get("threat_type", "unknown"),
                    incident_data.get("confidence", 0.0),
                    incident_data.get("severity", "LOW"),
                    incident_data.get("persons_involved", 0),
                    incident_data.get("description", ""),
                    incident_data.get("snapshot_path", ""),
                    incident_data.get("recording_path", ""),
                    incident_data.get("alert_sent", 0),
                    incident_data.get("acknowledged", 0),
                ))
                conn.commit()
                incident_id = cursor.lastrowid
                logger.info(
                    f"Incident logged: ID={incident_id}, "
                    f"type={incident_data.get('threat_type')}, "
                    f"camera={incident_data.get('camera_id')}"
                )
                return incident_id
            except sqlite3.Error as e:
                logger.error(f"Error logging incident: {e}")
                return -1
            finally:
                conn.close()

    def get_incidents(
        self,
        camera_id: Optional[str] = None,
        threat_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get incidents with optional filters."""
        with self._lock:
            conn = self._get_connection()
            try:
                query = "SELECT * FROM incidents WHERE 1=1"
                params: list[Any] = []

                if camera_id:
                    query += " AND camera_id = ?"
                    params.append(camera_id)
                if threat_type:
                    query += " AND threat_type = ?"
                    params.append(threat_type)
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except sqlite3.Error as e:
                logger.error(f"Error fetching incidents: {e}")
                return []
            finally:
                conn.close()

    def get_daily_stats(self, date: Optional[str] = None) -> dict[str, Any]:
        """Get threat counts by type and camera for a given date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT threat_type, COUNT(*) as count
                    FROM incidents
                    WHERE DATE(timestamp) = ?
                    GROUP BY threat_type
                """, (date,))
                by_type = {row["threat_type"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("""
                    SELECT camera_id, COUNT(*) as count
                    FROM incidents
                    WHERE DATE(timestamp) = ?
                    GROUP BY camera_id
                """, (date,))
                by_camera = {row["camera_id"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("""
                    SELECT COUNT(*) as total FROM incidents
                    WHERE DATE(timestamp) = ?
                """, (date,))
                total = cursor.fetchone()["total"]

                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM incidents
                    WHERE DATE(timestamp) = ?
                    GROUP BY severity
                """, (date,))
                by_severity = {row["severity"]: row["count"] for row in cursor.fetchall()}

                return {
                    "date": date,
                    "total_incidents": total,
                    "by_type": by_type,
                    "by_camera": by_camera,
                    "by_severity": by_severity,
                }
            except sqlite3.Error as e:
                logger.error(f"Error fetching daily stats: {e}")
                return {"date": date, "total_incidents": 0, "by_type": {}, "by_camera": {}, "by_severity": {}}
            finally:
                conn.close()

    def get_recent_incidents(self, n: int = 20) -> list[dict[str, Any]]:
        """Get the last N incidents."""
        return self.get_incidents(limit=n)

    def update_camera_status(self, camera_id: str, status_data: dict[str, Any]) -> None:
        """Update or insert camera status."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO camera_status (camera_id, last_seen, status, fps, frames_processed, threats_today)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(camera_id) DO UPDATE SET
                        last_seen = excluded.last_seen,
                        status = excluded.status,
                        fps = excluded.fps,
                        frames_processed = excluded.frames_processed,
                        threats_today = excluded.threats_today
                """, (
                    camera_id,
                    status_data.get("last_seen", datetime.now().isoformat()),
                    status_data.get("status", "offline"),
                    status_data.get("fps", 0.0),
                    status_data.get("frames_processed", 0),
                    status_data.get("threats_today", 0),
                ))
                conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Error updating camera status: {e}")
            finally:
                conn.close()

    def get_camera_status(self, camera_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Get status for one or all cameras."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if camera_id:
                    cursor.execute("SELECT * FROM camera_status WHERE camera_id = ?", (camera_id,))
                else:
                    cursor.execute("SELECT * FROM camera_status")
                return [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                logger.error(f"Error fetching camera status: {e}")
                return []
            finally:
                conn.close()

    def log_system_event(self, level: str, message: str, camera_id: Optional[str] = None) -> None:
        """Log a system event."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_logs (timestamp, level, message, camera_id)
                    VALUES (?, ?, ?, ?)
                """, (datetime.now().isoformat(), level, message, camera_id))
                conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Error logging system event: {e}")
            finally:
                conn.close()

    def get_system_logs(self, limit: int = 100, level: Optional[str] = None) -> list[dict[str, Any]]:
        """Get recent system logs."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if level:
                    cursor.execute(
                        "SELECT * FROM system_logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?",
                        (level, limit),
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT ?",
                        (limit,),
                    )
                return [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                logger.error(f"Error fetching system logs: {e}")
                return []
            finally:
                conn.close()

    def mark_incident_acknowledged(self, incident_id: int) -> bool:
        """Mark an incident as acknowledged."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE incidents SET acknowledged = 1 WHERE id = ?",
                    (incident_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                logger.error(f"Error acknowledging incident: {e}")
                return False
            finally:
                conn.close()

    def cleanup_old_records(self, retention_days: int = 30) -> int:
        """Delete records older than retention_days. Returns count deleted."""
        cutoff = (datetime.now() - timedelta(days=retention_days)).isoformat()
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM incidents WHERE timestamp < ?", (cutoff,))
                deleted_incidents = cursor.rowcount
                cursor.execute("DELETE FROM system_logs WHERE timestamp < ?", (cutoff,))
                deleted_logs = cursor.rowcount
                conn.commit()
                total = deleted_incidents + deleted_logs
                logger.info(f"Cleaned up {total} old records (incidents={deleted_incidents}, logs={deleted_logs})")
                return total
            except sqlite3.Error as e:
                logger.error(f"Error cleaning up records: {e}")
                return 0
            finally:
                conn.close()

    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database. Returns backup file path."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self._db_path.parent / f"safewatch_backup_{timestamp}.db")

        with self._lock:
            conn = self._get_connection()
            try:
                backup_conn = sqlite3.connect(backup_path)
                conn.backup(backup_conn)
                backup_conn.close()
                logger.info(f"Database backed up to {backup_path}")
                return backup_path
            except sqlite3.Error as e:
                logger.error(f"Database backup failed: {e}")
                return ""
            finally:
                conn.close()
