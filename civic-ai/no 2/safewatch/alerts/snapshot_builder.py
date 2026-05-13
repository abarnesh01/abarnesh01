import cv2
import numpy as np
import time
from pathlib import Path
from loguru import logger
from typing import Dict, Any

class SnapshotBuilder:
    """
    Renders high-quality security snapshots with metadata overlays.
    Saves snapshots to disk for Telegram alerts and database logging.
    """
    def __init__(self, output_dir: str = "recordings/snapshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, frame: np.ndarray, threat: Dict[str, Any], camera_name: str) -> str:
        """
        Creates a branded snapshot with threat details.
        Returns the path to the saved image.
        """
        canvas = frame.copy()
        h, w = canvas.shape[:2]
        
        # 1. Add Header Overlay
        severity = threat.get('severity', 'UNKNOWN')
        color = self._get_color(severity)
        
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), color, -1)
        cv2.addWeighted(overlay, 0.7, canvas, 0.3, 0, canvas)
        
        # 2. Add Threat Text
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(canvas, f"SAFEWATCH - {threat['type']}", (20, 40), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
        
        # 3. Add Metadata Footer
        cv2.rectangle(canvas, (0, h-40), (w, h), (0, 0, 0), -1)
        meta_text = f"CAM: {camera_name} | {timestamp} | SEVERITY: {severity} | CONF: {threat['confidence']:.2f}"
        cv2.putText(canvas, meta_text, (10, h-12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # 4. Save File
        filename = f"{threat['type']}_{int(time.time())}.jpg"
        filepath = self.output_dir / filename
        cv2.imwrite(str(filepath), canvas)
        
        logger.debug(f"Snapshot created: {filepath}")
        return str(filepath)

    def _get_color(self, severity: str) -> tuple:
        colors = {
            "LOW": (0, 255, 255),
            "MEDIUM": (0, 165, 255),
            "HIGH": (0, 0, 255),
            "CRITICAL": (128, 0, 128)
        }
        return colors.get(severity, (100, 100, 100))
