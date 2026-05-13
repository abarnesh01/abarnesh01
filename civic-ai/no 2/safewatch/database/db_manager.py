import sqlite3
import threading
from pathlib import Path
from loguru import logger
from datetime import datetime

class DatabaseManager:
    """Enterprise-grade SQLite database manager with thread-safety."""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
            return cls._instance

    def __init__(self, db_path: str = "data/safewatch.db"):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._initialize_db()
        self._initialized = True
        logger.info(f"DatabaseManager initialized at {self.db_path}")

    def _get_connection(self):
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _initialize_db(self):
        """Creates necessary tables if they don't exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                camera_id TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence REAL,
                snapshot_path TEXT,
                status TEXT DEFAULT 'NEW',
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS camera_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                camera_id TEXT NOT NULL,
                status TEXT NOT NULL,
                fps REAL,
                latency REAL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents(timestamp);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_incidents_camera ON incidents(camera_id);
            """
        ]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            for query in queries:
                cursor.execute(query)
            conn.commit()
            logger.debug("Database tables initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            conn.rollback()

    def execute(self, query: str, params: tuple = ()):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Database query execution failed: {e} | Query: {query}")
            conn.rollback()
            raise

    def fetch_all(self, query: str, params: tuple = ()):
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()):
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        if hasattr(self._local, "connection"):
            self._local.connection.close()
            del self._local.connection
            logger.info("Database connection closed.")
