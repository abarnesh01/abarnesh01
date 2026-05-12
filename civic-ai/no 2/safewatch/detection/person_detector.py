"""
SafeWatch — Person Detector
YOLOv8-based person detection with IoU-based tracking for consistent IDs.
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Optional

import cv2
import numpy as np
from loguru import logger


@dataclass
class Person:
    """Detected person with bounding box and tracking info."""
    id: int
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    center: tuple[int, int]
    area: int
    width: int
    height: int

    def __repr__(self) -> str:
        return f"Person(id={self.id}, conf={self.confidence:.2f}, center={self.center})"


class PersonDetector:
    """YOLOv8-based person detector with simple IoU tracking."""

    def __init__(
        self,
        model_path: str = "models/yolov8n.pt",
        confidence: float = 0.5,
        classes: list[int] = None,
        max_tracked: int = 10,
    ) -> None:
        self._model_path = model_path
        self._confidence = confidence
        self._classes = classes if classes is not None else [0]
        self._max_tracked = max_tracked
        self._model = None
        self._lock = threading.Lock()
        self._next_id = 1
        self._prev_persons: list[Person] = []
        self._iou_threshold = 0.3
        self._load_model()

    def __repr__(self) -> str:
        return f"PersonDetector(model='{self._model_path}', conf={self._confidence})"

    def _load_model(self) -> None:
        """Load YOLOv8 model (downloads automatically if not present)."""
        try:
            from ultralytics import YOLO
            self._model = YOLO(self._model_path)
            logger.info(f"YOLOv8 model loaded: {self._model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            logger.warning("PersonDetector will attempt re-download of yolov8n.pt")
            try:
                from ultralytics import YOLO
                self._model = YOLO("yolov8n.pt")
                logger.info("YOLOv8n downloaded and loaded successfully")
            except Exception as e2:
                logger.error(f"Failed to download YOLOv8 model: {e2}")
                self._model = None

    def _compute_iou(self, box1: tuple, box2: tuple) -> float:
        """Compute Intersection over Union between two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        if inter_area == 0:
            return 0.0

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = area1 + area2 - inter_area

        if union_area == 0:
            return 0.0
        return inter_area / union_area

    def _assign_ids(self, detections: list[dict[str, Any]]) -> list[Person]:
        """Assign consistent IDs using IoU matching with previous frame."""
        persons: list[Person] = []
        used_prev: set[int] = set()

        for det in detections:
            bbox = det["bbox"]
            best_iou = 0.0
            best_prev_idx = -1

            for idx, prev in enumerate(self._prev_persons):
                if idx in used_prev:
                    continue
                iou = self._compute_iou(bbox, prev.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_prev_idx = idx

            if best_iou >= self._iou_threshold and best_prev_idx >= 0:
                person_id = self._prev_persons[best_prev_idx].id
                used_prev.add(best_prev_idx)
            else:
                person_id = self._next_id
                self._next_id += 1

            x1, y1, x2, y2 = bbox
            person = Person(
                id=person_id,
                bbox=bbox,
                confidence=det["confidence"],
                center=((x1 + x2) // 2, (y1 + y2) // 2),
                area=(x2 - x1) * (y2 - y1),
                width=x2 - x1,
                height=y2 - y1,
            )
            persons.append(person)

        self._prev_persons = persons[:self._max_tracked]
        return persons

    def detect(self, frame: np.ndarray) -> list[Person]:
        """Detect persons in a frame. Returns list of Person objects."""
        if self._model is None:
            return []

        with self._lock:
            try:
                results = self._model(
                    frame,
                    conf=self._confidence,
                    classes=self._classes,
                    verbose=False,
                )

                detections: list[dict[str, Any]] = []
                for result in results:
                    if result.boxes is None:
                        continue
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        conf = float(box.conf[0].cpu().numpy())
                        detections.append({
                            "bbox": (int(x1), int(y1), int(x2), int(y2)),
                            "confidence": conf,
                        })

                persons = self._assign_ids(detections)
                return persons[:self._max_tracked]

            except Exception as e:
                logger.error(f"Person detection error: {e}")
                return []

    def draw_detections(self, frame: np.ndarray, persons: list[Person]) -> np.ndarray:
        """Draw bounding boxes and IDs on frame."""
        annotated = frame.copy()
        for person in persons:
            x1, y1, x2, y2 = person.bbox
            color = (0, 255, 0)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            label = f"ID:{person.id} {person.confidence:.0%}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(
                annotated,
                (x1, y1 - label_size[1] - 8),
                (x1 + label_size[0] + 4, y1),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
        return annotated
