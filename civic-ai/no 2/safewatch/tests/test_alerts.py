"""SafeWatch — Alert Module Tests."""

import time
import numpy as np


class TestAlerts:
    """Tests for alert modules."""

    def test_snapshot_builder(self):
        """Test SnapshotBuilder creates valid JPEG bytes."""
        from alerts.snapshot_builder import SnapshotBuilder

        builder = SnapshotBuilder()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 50, 80)

        threat_event = {
            "threat_type": "fight",
            "confidence": 0.92,
            "severity": "HIGH",
            "persons_involved": 2,
            "person_ids": [1, 2],
            "location_bbox": (100, 100, 300, 400),
            "description": "Test fight detection",
        }

        jpeg_bytes = builder.build(
            frame=frame,
            threat_event=threat_event,
            camera_id="CAM-TEST",
            timestamp=time.time(),
            camera_name="Test Camera",
        )

        assert isinstance(jpeg_bytes, bytes)
        assert len(jpeg_bytes) > 100
        # JPEG magic bytes
        assert jpeg_bytes[:2] == b'\xff\xd8'

    def test_telegram_bot_disabled(self):
        """Test TelegramBot gracefully handles missing token."""
        from alerts.telegram_bot import SafeWatchTelegramBot

        bot = SafeWatchTelegramBot({
            "enabled": True,
            "bot_token": "",
            "agents": {
                "test_agent": {
                    "chat_id": "12345",
                    "name": "Test",
                    "cameras": ["CAM-01"],
                },
            },
        })

        assert not bot._enabled or bot._bot is None
        assert "SafeWatchTelegramBot" in repr(bot)

    def test_alert_manager_cooldown(self):
        """Test AlertManager cooldown prevents duplicate alerts."""
        from alerts.alert_manager import AlertManager
        from alerts.telegram_bot import SafeWatchTelegramBot
        from database.db_manager import DatabaseManager
        from database.incident_logger import IncidentLogger

        db = DatabaseManager(":memory:")
        il = IncidentLogger(db)
        bot = SafeWatchTelegramBot({"enabled": False, "agents": {}})

        config = {
            "telegram": {"alert_cooldown_seconds": 30, "send_snapshot": False, "agents": {}},
            "cameras": [{"id": "CAM-01", "name": "Test Cam"}],
        }

        manager = AlertManager(bot, il, config)

        # First check should pass
        assert manager._check_cooldown("CAM-01", "fight", time.time())
        # Second check within cooldown should fail
        assert not manager._check_cooldown("CAM-01", "fight", time.time())
        # Different threat type should pass
        assert manager._check_cooldown("CAM-01", "fall", time.time())

    def test_database_operations(self):
        """Test DatabaseManager CRUD operations."""
        from database.db_manager import DatabaseManager

        db = DatabaseManager(":memory:")

        # Log incident
        incident_id = db.log_incident({
            "camera_id": "CAM-01",
            "timestamp": "2024-01-15T10:30:00",
            "threat_type": "fight",
            "confidence": 0.92,
            "severity": "HIGH",
            "persons_involved": 2,
            "description": "Test fight",
        })
        assert incident_id > 0

        # Fetch incidents
        incidents = db.get_incidents(camera_id="CAM-01")
        assert len(incidents) == 1
        assert incidents[0]["threat_type"] == "fight"

        # Daily stats
        stats = db.get_daily_stats("2024-01-15")
        assert stats["total_incidents"] == 1

        # Acknowledge
        assert db.mark_incident_acknowledged(incident_id)


if __name__ == "__main__":
    t = TestAlerts()
    t.test_snapshot_builder()
    print("✅ test_snapshot_builder passed")
    t.test_telegram_bot_disabled()
    print("✅ test_telegram_bot_disabled passed")
    t.test_alert_manager_cooldown()
    print("✅ test_alert_manager_cooldown passed")
    t.test_database_operations()
    print("✅ test_database_operations passed")
    print("\nAll alert tests passed! ✅")
