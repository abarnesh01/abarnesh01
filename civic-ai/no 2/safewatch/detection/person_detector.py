import cv2
import numpy as np
from ultralytics import YOLO
from loguru import logger
from typing import List, Dict, Any

class PersonDetector:
    """YOLOv8 based person detection and tracking optimized for CPU."""

    def __init__(self, model_path: str = "models/yolov8n.pt", conf: float = 0.5):
        self.model_path = model_path
        self.conf = conf
        try:
            self.model = YOLO(model_path)
            logger.info(f"YOLOv8 model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            # Fallback to downloading if not present (handled by ultralytics)
            self.model = YOLO("yolov8n.pt") 

    def detect(self, frame: cv2.Mat) -> List[Dict[str, Any]]:
        """Detects and tracks persons in the frame."""
        # Run tracking (persistent IDs)
        results = self.model.track(
            frame, 
            persist=True, 
            classes=[0],  # Person only
            conf=self.conf,
            verbose=False,
            device='cpu'
        )

        detections = []
        if not results or not results[0].boxes:
            return detections

        boxes = results[0].boxes
        for box in boxes:
            # box.xyxy: [x1, y1, x2, y2]
            # box.id: tracking ID
            # box.conf: confidence score
            
            coords = box.xyxy[0].cpu().numpy().astype(int)
            track_id = int(box.id[0].cpu().numpy()) if box.id is not None else -1
            confidence = float(box.conf[0].cpu().numpy())

            detections.append({
                "id": track_id,
                "bbox": coords,
                "confidence": confidence,
                "label": "person"
            })

        return detections

    def draw_detections(self, frame: cv2.Mat, detections: List[Dict[str, Any]]):
        """Renders bounding boxes and IDs on the frame."""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {det['id']} {det['confidence']:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
