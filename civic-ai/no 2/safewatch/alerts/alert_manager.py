from typing import Dict, Any, Optional
from loguru import logger
from .telegram_bot import TelegramAlertBot
from .snapshot_builder import SnapshotBuilder
from database.incident_logger import IncidentLogger

class AlertManager:
    """Orchestrates snapshots, database logging, and Telegram alerts."""

    def __init__(self, config: Dict[str, Any], incident_logger: IncidentLogger):
        self.config = config
        self.incident_logger = incident_logger
        self.snapshot_builder = SnapshotBuilder(config.get("system", {}).get("snapshots_dir", "recordings/snapshots"))
        
        tg_config = config.get("alerts", {})
        self.telegram_bot = TelegramAlertBot(
            token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
        )
        self.enabled = tg_config.get("telegram_enabled", True)

    def trigger(self, event: Any, frame: Optional[Any] = None):
        """
        Handles a ThreatEvent: build snapshot, log to DB, send Telegram.
        """
        logger.warning(f"ALERT TRIGGERED: {event.threat_type} ({event.severity}) on {event.camera_id}")

        snapshot_path = None
        if frame is not None and self.config.get("alerts", {}).get("snapshot_enabled", True):
            snapshot_path = self.snapshot_builder.build(
                frame, event.threat_type, event.severity, event.confidence, event.camera_id
            )

        # 1. Log to Database
        self.incident_logger.log_incident(
            camera_id=event.camera_id,
            threat_type=event.threat_type,
            severity=event.severity,
            confidence=event.confidence,
            snapshot_path=snapshot_path,
            metadata=event.metadata
        )

        # 2. Send Telegram Alert
        if self.enabled:
            msg = (
                f"🚨 <b>THREAT DETECTED</b>\n"
                f"Type: {event.threat_type}\n"
                f"Severity: {event.severity}\n"
                f"Confidence: {event.confidence:.2f}\n"
                f"Camera: {event.camera_id}\n"
                f"Description: {event.description}"
            )
            self.telegram_bot.dispatch_sync(msg, snapshot_path, event.severity)

import os
