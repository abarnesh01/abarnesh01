import cv2
import numpy as np
from ultralytics import YOLO
from loguru import logger
from typing import List, Dict, Any, Tuple

class PersonDetector:
    """
    Wraps YOLOv8 for optimized person detection and tracking.
    Uses CPU-optimized inference.
    """
    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.25):
        logger.info(f"Loading YOLOv8 model from {model_path}...")
        try:
            self.model = YOLO(model_path)
            self.conf = conf
            self.person_class_id = 0 # YOLO class for 'person'
            logger.success("YOLOv8 loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs inference on a single frame and returns a list of detected persons.
        Returns format: [{'bbox': [x1, y1, x2, y2], 'conf': 0.9, 'id': 1}, ...]
        """
        # Run tracking (persistent IDs)
        results = self.model.track(
            frame, 
            persist=True, 
            classes=[self.person_class_id], 
            conf=self.conf,
            verbose=False,
            device='cpu'
        )
        
        detections = []
        if results and len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                # Extract coordinates
                b = box.xyxy[0].cpu().numpy() # [x1, y1, x2, y2]
                conf = box.conf[0].cpu().item()
                
                # Get tracking ID if available
                track_id = int(box.id[0].cpu().item()) if box.id is not None else -1
                
                detections.append({
                    "bbox": b.astype(int).tolist(),
                    "confidence": conf,
                    "id": track_id,
                    "class": "person"
                })
                
        return detections

    @staticmethod
    def draw_detections(frame: np.ndarray, detections: List[Dict[str, Any]]):
        """Visualizes bounding boxes and IDs on the frame."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            track_id = det['id']
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw ID label
            label = f"ID: {track_id}" if track_id != -1 else "Person"
            cv2.putText(frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
