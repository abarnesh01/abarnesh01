"""
SafeWatch — Alert Manager
Coordinates between ThreatEngine and TelegramBot with cooldown and queuing.
"""

import threading
import time
from collections import defaultdict
from typing import Any, Optional

import numpy as np
from loguru import logger

from alerts.snapshot_builder import SnapshotBuilder
from alerts.telegram_bot import SafeWatchTelegramBot
from database.incident_logger import IncidentLogger
from threats.threat_engine import ThreatEvent, ThreatReport


class AlertManager:
    """Coordinates threat reports to Telegram alerts with cooldown and routing."""

    def __init__(
        self,
        telegram_bot: SafeWatchTelegramBot,
        incident_logger: IncidentLogger,
        config: dict[str, Any],
    ) -> None:
        self._bot = telegram_bot
        self._logger = incident_logger
        self._snapshot_builder = SnapshotBuilder()
        self._cooldown_seconds = config.get("telegram", {}).get("alert_cooldown_seconds", 30)
        self._send_snapshot = config.get("telegram", {}).get("send_snapshot", True)
        self._lock = threading.Lock()
        self._cooldowns: dict[tuple[str, str], float] = {}
        self._alert_queue: list[dict[str, Any]] = []
        self._active_alerts: list[dict[str, Any]] = []
        self._next_alert_id = 1

        # Camera -> agent mapping from config
        self._camera_agents: dict[str, list[str]] = {}
        agents_cfg = config.get("telegram", {}).get("agents", {})
        for agent_id, agent_data in agents_cfg.items():
            for cam_id in agent_data.get("cameras", []):
                if cam_id not in self._camera_agents:
                    self._camera_agents[cam_id] = []
                self._camera_agents[cam_id].append(agent_id)

        # Camera name lookup
        self._camera_names: dict[str, str] = {}
        for cam in config.get("cameras", []):
            self._camera_names[cam["id"]] = cam.get("name", cam["id"])

        logger.info(f"AlertManager initialized (cooldown={self._cooldown_seconds}s)")

    def __repr__(self) -> str:
        return f"AlertManager(active_alerts={len(self._active_alerts)})"

    def process_threat_report(
        self,
        threat_report: ThreatReport,
        frame: Optional[np.ndarray] = None,
    ) -> list[int]:
        """Process a threat report: build snapshots, log incidents, send alerts.
        
        Returns list of incident IDs that were logged.
        """
        incident_ids: list[int] = []

        for threat in threat_report.threats_detected:
            camera_id = threat_report.camera_id
            timestamp = threat.timestamp

            # Check cooldown
            if not self._check_cooldown(camera_id, threat.threat_type, timestamp):
                continue

            # Build snapshot
            snapshot_bytes = None
            snapshot_path = ""
            if frame is not None and self._send_snapshot:
                try:
                    snapshot_bytes = self._snapshot_builder.build(
                        frame=frame,
                        threat_event=threat.to_dict(),
                        camera_id=camera_id,
                        timestamp=timestamp,
                        camera_name=self._camera_names.get(camera_id, camera_id),
                    )
                    snapshot_path = self._snapshot_builder.save_snapshot(
                        snapshot_bytes, camera_id, timestamp
                    )
                except Exception as e:
                    logger.error(f"Snapshot build error: {e}")

            # Log to database
            threat_dict = threat.to_dict()
            threat_dict["alert_sent"] = 1
            incident_id = self._logger.log_threat(
                threat_event=threat_dict,
                camera_id=camera_id,
                snapshot_path=snapshot_path,
            )
            if incident_id > 0:
                incident_ids.append(incident_id)

            # Send Telegram alert
            try:
                camera_name = self._camera_names.get(camera_id, camera_id)
                self._bot.run_async(
                    self._bot.send_threat_alert(
                        threat_event=threat_dict,
                        camera_id=camera_id,
                        camera_name=camera_name,
                        snapshot_bytes=snapshot_bytes,
                    )
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")

            # Track active alert
            with self._lock:
                alert_record = {
                    "alert_id": self._next_alert_id,
                    "incident_id": incident_id,
                    "camera_id": camera_id,
                    "threat_type": threat.threat_type,
                    "severity": threat.severity,
                    "confidence": threat.confidence,
                    "timestamp": timestamp,
                    "acknowledged": False,
                }
                self._active_alerts.append(alert_record)
                self._next_alert_id += 1

                # Keep only last 100 alerts
                if len(self._active_alerts) > 100:
                    self._active_alerts = self._active_alerts[-100:]

        return incident_ids

    def _check_cooldown(self, camera_id: str, threat_type: str, timestamp: float) -> bool:
        """Check if a threat type is in cooldown for a camera."""
        key = (camera_id, threat_type)
        with self._lock:
            last_time = self._cooldowns.get(key, 0)
            if timestamp - last_time < self._cooldown_seconds:
                return False
            self._cooldowns[key] = timestamp
            return True

    def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge an alert by ID."""
        with self._lock:
            for alert in self._active_alerts:
                if alert["alert_id"] == alert_id:
                    alert["acknowledged"] = True
                    incident_id = alert.get("incident_id", -1)
                    if incident_id > 0:
                        self._logger.acknowledge(incident_id)
                    logger.info(f"Alert {alert_id} acknowledged")
                    return True
        return False

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get list of recent unacknowledged alerts."""
        with self._lock:
            return [a for a in self._active_alerts if not a.get("acknowledged", False)]

    def get_all_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get all recent alerts."""
        with self._lock:
            return list(self._active_alerts[-limit:])
