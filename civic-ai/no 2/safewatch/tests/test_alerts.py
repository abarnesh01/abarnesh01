import pytest
import os
from pathlib import Path
from safewatch.alerts.snapshot_builder import SnapshotBuilder

def test_snapshot_builder_directory():
    test_dir = "recordings/test_snapshots"
    builder = SnapshotBuilder(output_dir=test_dir)
    assert Path(test_dir).exists()
    # Cleanup
    if Path(test_dir).exists():
        os.rmdir(test_dir)

def test_alert_manager_init():
    # Mocking config and logger would be better, but testing init for now
    from safewatch.alerts.alert_manager import AlertManager
    from safewatch.database.incident_logger import IncidentLogger
    from safewatch.database.db_manager import DatabaseManager
    
    db = DatabaseManager(":memory:")
    logger = IncidentLogger(db)
    config = {"alerts": {"telegram_enabled": False}, "system": {"snapshots_dir": "recordings/snapshots"}}
    
    manager = AlertManager(config, logger)
    assert manager.enabled == False
