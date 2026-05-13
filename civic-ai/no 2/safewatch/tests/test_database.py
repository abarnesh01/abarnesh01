import pytest
from safewatch.database.db_manager import DatabaseManager
from safewatch.database.incident_logger import IncidentLogger

def test_db_init():
    db = DatabaseManager(":memory:")
    assert db is not None
    db.close()

def test_incident_logging():
    db = DatabaseManager(":memory:")
    logger = IncidentLogger(db)
    
    logger.log_incident("CAM-01", "Fight", "HIGH", "path/to/snap.jpg")
    
    incidents = db.fetch_all("SELECT * FROM incidents")
    assert len(incidents) == 1
    assert incidents[0]["threat_type"] == "Fight"
    db.close()
