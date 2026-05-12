"""
SafeWatch — Snapshot Builder
Builds annotated alert snapshots with threat overlays for Telegram alerts.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger
from PIL import Image, ImageDraw, ImageFont


class SnapshotBuilder:
    """Builds annotated threat snapshot images for alert dispatch."""

    SEVERITY_COLORS = {
        "LOW": (255, 255, 0),
        "MEDIUM": (255, 165, 0),
        "HIGH": (255, 0, 0),
        "CRITICAL": (128, 0, 128),
    }

    def __init__(self) -> None:
        self._font = None
        self._font_small = None
        try:
            self._font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self._font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except (IOError, OSError):
            self._font = ImageFont.load_default()
            self._font_small = ImageFont.load_default()
        logger.info("SnapshotBuilder initialized")

    def __repr__(self) -> str:
        return "SnapshotBuilder()"

    def build(
        self,
        frame: np.ndarray,
        threat_event: dict[str, Any],
        camera_id: str,
        timestamp: float,
        camera_name: str = "",
    ) -> bytes:
        """Build an annotated snapshot. Returns JPEG bytes."""
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)

        w, h = pil_img.size
        severity = threat_event.get("severity", "MEDIUM")
        threat_type = threat_event.get("threat_type", "unknown")
        confidence = threat_event.get("confidence", 0.0)

        # 1. Draw border based on severity
        border_color = self.SEVERITY_COLORS.get(severity, (255, 165, 0))
        border_width = 6 if severity in ("HIGH", "CRITICAL") else 4
        for i in range(border_width):
            draw.rectangle(
                [i, i, w - 1 - i, h - 1 - i],
                outline=border_color,
            )

        # 2. Threat label banner at top
        banner_height = 35
        banner_color = border_color + (200,)  # Semi-transparent
        draw.rectangle([0, 0, w, banner_height], fill=border_color)
        threat_label = f"⚠️ {threat_type.upper()} DETECTED — {confidence:.0%} confidence"
        draw.text(
            (10, 8),
            threat_label,
            fill=(255, 255, 255),
            font=self._font,
        )

        # 3. Bounding boxes around involved persons
        bbox = threat_event.get("location_bbox", (0, 0, 0, 0))
        if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            draw.rectangle(
                [bbox[0], bbox[1], bbox[2], bbox[3]],
                outline=border_color,
                width=3,
            )
            person_ids = threat_event.get("person_ids", [])
            if person_ids:
                id_label = f"ID: {', '.join(str(p) for p in person_ids)}"
                draw.text(
                    (bbox[0] + 2, bbox[1] - 18),
                    id_label,
                    fill=border_color,
                    font=self._font_small,
                )

        # 4. Timestamp overlay at bottom right
        dt_str = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
        ts_bbox = draw.textbbox((0, 0), dt_str, font=self._font_small)
        ts_width = ts_bbox[2] - ts_bbox[0]
        draw.rectangle(
            [w - ts_width - 15, h - 28, w, h],
            fill=(0, 0, 0, 180),
        )
        draw.text(
            (w - ts_width - 10, h - 25),
            dt_str,
            fill=(255, 255, 255),
            font=self._font_small,
        )

        # 5. Camera name at bottom left
        cam_label = camera_name if camera_name else camera_id
        draw.rectangle([0, h - 28, len(cam_label) * 9 + 15, h], fill=(0, 0, 0, 180))
        draw.text(
            (5, h - 25),
            cam_label,
            fill=(200, 200, 200),
            font=self._font_small,
        )

        # 6. SafeWatch watermark
        draw.text(
            (w - 100, banner_height + 5),
            "SafeWatch",
            fill=(255, 255, 255, 100),
            font=self._font_small,
        )

        # Convert to JPEG bytes
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=85)
        jpeg_bytes = buffer.getvalue()
        buffer.close()

        return jpeg_bytes

    def save_snapshot(
        self,
        jpeg_bytes: bytes,
        camera_id: str,
        timestamp: float,
        output_dir: str = "recordings",
    ) -> str:
        """Save snapshot to disk. Returns file path."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        dt_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{camera_id}_{dt_str}.jpg"
        filepath = out_dir / filename

        with open(filepath, "wb") as f:
            f.write(jpeg_bytes)

        logger.debug(f"Snapshot saved: {filepath}")
        return str(filepath)
