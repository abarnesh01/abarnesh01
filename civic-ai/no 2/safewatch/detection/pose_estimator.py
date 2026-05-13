import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger

class PoseEstimator:
    """MediaPipe based 3D skeleton pose estimation."""

    def __init__(self, 
                 static_image_mode: bool = False,
                 model_complexity: int = 1,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        logger.info("MediaPipe Pose Estimator initialized.")

    def estimate(self, frame: cv2.Mat, bbox: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Estimates pose landmarks. 
        If bbox is provided, it crops the person for better accuracy (optional optimization).
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        landmarks_data = []
        if results.pose_landmarks:
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks_data.append({
                    "name": self.mp_pose.PoseLandmark(idx).name,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })
        
        return {
            "landmarks": landmarks_data,
            "raw": results.pose_landmarks,
            "world_landmarks": results.pose_world_landmarks
        }

    def draw_pose(self, frame: cv2.Mat, results: Dict[str, Any]):
        """Renders the skeleton on the frame."""
        if results["raw"]:
            self.mp_draw.draw_landmarks(
                frame,
                results["raw"],
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        return frame

    def calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculates the angle between three points."""
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
