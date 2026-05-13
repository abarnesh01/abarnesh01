import os
from pathlib import Path
from loguru import logger

def prepare_directories():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)
    logger.info("Dataset directories initialized.")

if __name__ == "__main__":
    prepare_directories()
    logger.info("Dataset downloader ready. (Manual download required for RWF-2000 due to size).")
