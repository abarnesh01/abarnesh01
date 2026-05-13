import cv2
import numpy as np
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

class SnapshotBuilder:
    """Renders professional security snapshots with threat banners and overlays."""

    def __init__(self, output_dir: str = "recordings/snapshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.watermark = "SafeWatch AI - Production Build"

    def build(self, 
              frame: cv2.Mat, 
              threat_type: str, 
              severity: str, 
              confidence: float,
              camera_name: str) -> str:
        """
        Creates an annotated snapshot and saves it to disk.
        Returns the file path.
        """
        canvas = frame.copy()
        h, w = canvas.shape[:2]

        # Severity Colors (BGR)
        colors = {
            "SAFE": (0, 255, 0),
            "LOW": (0, 255, 255),
            "MEDIUM": (0, 165, 255),
            "HIGH": (0, 0, 255),
            "CRITICAL": (128, 0, 128)
        }
        color = colors.get(severity, (255, 255, 255))

        # 1. Draw Severity Border
        cv2.rectangle(canvas, (0, 0), (w, h), color, 10)

        # 2. Add Top Banner
        cv2.rectangle(canvas, (0, 0), (w, 60), color, -1)
        text = f"ALERT: {threat_type} | SEVERITY: {severity} | CONF: {confidence:.2f}"
        cv2.putText(canvas, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 3. Add Info Footer
        cv2.rectangle(canvas, (0, h - 40), (w, h), (0, 0, 0), -1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"CAM: {camera_name} | {timestamp} | {self.watermark}"
        cv2.putText(canvas, footer_text, (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Save snapshot
        filename = f"{threat_type.lower()}_{int(time.time())}.jpg"
        filepath = self.output_dir / filename
        cv2.imwrite(str(filepath), canvas)
        
        logger.debug(f"Snapshot created: {filepath}")
        return str(filepath)
