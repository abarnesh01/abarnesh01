import cv2
import mediapipe as mp
import numpy as np
from loguru import logger
from typing import List, Dict, Any, Optional

class PoseEstimator:
    """
    Leverages MediaPipe for real-time human pose landmark detection.
    Extracts 33 skeletal landmarks per person.
    """
    def __init__(self, static_image_mode: bool = False, min_detection_confidence: float = 0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=1, # 0=Lite, 1=Full, 2=Heavy. Full is good balance for CPU.
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        logger.info("MediaPipe Pose Estimator initialized.")

    def estimate(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[int, Any]:
        """
        Estimates pose for each detected person.
        Returns a dictionary mapping track_id to landmark list.
        """
        pose_results = {}
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            track_id = det['id']
            
            # Crop frame to person bounding box (with padding)
            h, w = frame.shape[:2]
            pad = 20
            px1, py1 = max(0, x1 - pad), max(0, y1 - pad)
            px2, py2 = min(w, x2 + pad), min(h, y2 + pad)
            
            person_roi = frame[py1:py2, px1:px2]
            if person_roi.size == 0:
                continue
                
            # Convert to RGB for MediaPipe
            roi_rgb = cv2.cvtColor(person_roi, cv2.COLOR_BGR2RGB)
            results = self.pose.process(roi_rgb)
            
            if results.pose_landmarks:
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    # Map ROI coordinates back to full frame
                    landmarks.append({
                        'x': lm.x * (px2 - px1) + px1,
                        'y': lm.y * (py2 - py1) + py1,
                        'z': lm.z,
                        'visibility': lm.visibility
                    })
                pose_results[track_id] = landmarks
                
        return pose_results

    def draw_poses(self, frame: np.ndarray, pose_results: Dict[int, Any]):
        """Renders skeleton overlays on the frame."""
        for track_id, landmarks in pose_results.items():
            # Convert our landmark dict back to MediaPipe format for drawing
            # This is a bit tricky, easier to just manually draw lines
            
            # Key points indices for drawing
            connections = self.mp_pose.POSE_CONNECTIONS
            
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    p1 = (int(landmarks[start_idx]['x']), int(landmarks[start_idx]['y']))
                    p2 = (int(landmarks[end_idx]['x']), int(landmarks[end_idx]['y']))
                    
                    if landmarks[start_idx]['visibility'] > 0.5 and landmarks[end_idx]['visibility'] > 0.5:
                        cv2.line(frame, p1, p2, (255, 255, 255), 2)
                        cv2.circle(frame, p1, 3, (0, 0, 255), -1)
                        cv2.circle(frame, p2, 3, (0, 0, 255), -1)
        return frame
