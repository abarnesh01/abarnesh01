import sqlite3
import threading
from pathlib import Path
from loguru import logger
from typing import Optional, List, Any, Dict

class DatabaseManager:
    """
    Thread-safe Singleton Database Manager for SafeWatch.
    Handles connections and basic CRUD operations for SQLite.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
            return cls._instance

    def __init__(self, db_path: str = "database/safewatch.db"):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = True
        self._local = threading.local()
        
        logger.info(f"DatabaseManager initialized at {self.db_path}")
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a thread-local database connection."""
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _create_tables(self):
        """Initializes the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    camera_id INTEGER,
                    camera_name TEXT,
                    threat_type TEXT,
                    severity TEXT,
                    confidence REAL,
                    snapshot_path TEXT,
                    video_path TEXT,
                    status TEXT DEFAULT 'OPEN',
                    assigned_to TEXT,
                    metadata TEXT
                )
            """)
            
            # Camera Health table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS camera_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id INTEGER UNIQUE,
                    camera_name TEXT,
                    status TEXT,
                    last_seen DATETIME,
                    error_msg TEXT
                )
            """)
            
            # System Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            conn.commit()
            logger.debug("Database tables verified/created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create database tables: {e}")
            conn.rollback()

    def execute(self, query: str, params: tuple = ()) -> bool:
        """Executes a non-returning query (INSERT, UPDATE, DELETE)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database execute error: {e} | Query: {query}")
            conn.rollback()
            return False

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a returning query (SELECT) and returns all results."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database fetch_all error: {e} | Query: {query}")
            return []

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes a returning query (SELECT) and returns the first result."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Database fetch_one error: {e} | Query: {query}")
            return None

    def close(self):
        """Closes the current thread's connection."""
        if hasattr(self._local, "connection"):
            self._local.connection.close()
            del self._local.connection
            logger.debug("Database connection closed for current thread.")

# Global instance for easy access
db = DatabaseManager()
