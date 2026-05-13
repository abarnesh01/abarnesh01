import os
import requests
from pathlib import Path
from loguru import logger

def download_file(url: str, dest_path: Path):
    if dest_path.exists():
        logger.info(f"File already exists: {dest_path}")
        return
    
    logger.info(f"Downloading {url} to {dest_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info("Download complete.")

def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # YOLOv8n (Smallest version for CPU efficiency)
    yolo_url = "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"
    download_file(yolo_url, models_dir / "yolov8n.pt")
    
    logger.info("All essential models are ready.")

if __name__ == "__main__":
    main()
