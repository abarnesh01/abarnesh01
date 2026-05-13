from typing import Dict, Any, Optional
from alerts.telegram_bot import TelegramAlertBot
from database.incident_logger import IncidentLogger
from loguru import logger

class AlertManager:
    """
    Coordinates alert dispatching across multiple channels.
    Integrates with Database and Telegram.
    """
    def __init__(self, telegram_enabled: bool = True):
        self.telegram = TelegramAlertBot() if telegram_enabled else None
        self.incident_logger = IncidentLogger()

    def process_threat(self, threat: Dict[str, Any], camera_id: int, camera_name: str, snapshot_path: Optional[str] = None):
        """
        Logs the threat to the database and dispatches external alerts.
        """
        # 1. Log to DB
        incident_id = self.incident_logger.log_incident(
            camera_id=camera_id,
            camera_name=camera_name,
            threat_type=threat['type'],
            severity=threat['severity'],
            confidence=threat['confidence'],
            snapshot_path=snapshot_path,
            metadata={"ids": threat.get('ids', []), "description": threat.get('description', '')}
        )
        
        # 2. Dispatch External Alerts (Telegram)
        if self.telegram:
            message = (
                f"🚨 *SAFEWATCH ALERT* 🚨\n\n"
                f"*Type:* {threat['type']}\n"
                f"*Severity:* {threat['severity']}\n"
                f"*Confidence:* {threat['confidence']:.2f}\n"
                f"*Camera:* {camera_name}\n"
                f"*Incident ID:* {incident_id}\n\n"
                f"📝 {threat.get('description', '')}"
            )
            
            self.telegram.dispatch_alert(message, snapshot_path)
            
        logger.info(f"Alert processed for {threat['type']} at {camera_name}")
