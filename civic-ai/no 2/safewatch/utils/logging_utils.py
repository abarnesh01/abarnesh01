import sys
from loguru import logger

def configure_logger(log_file: str = "logs/system.log"):
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, rotation="10 MB", level="DEBUG")
    logger.info(f"System logger configured. Logs saved to {log_file}")
