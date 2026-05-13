import os
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from loguru import logger
import json

class DatasetPrep:
    """Prepares skeleton landmarks from video datasets for classifier training."""

    def __init__(self, output_path: str = "training/data/processed_landmarks.json"):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.mp_pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)

    def extract_landmarks_from_video(self, video_path: str, label: str):
        """Processes a video and returns a list of frame-by-frame landmarks."""
        cap = cv2.VideoCapture(video_path)
        video_data = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = []
                # Extract first 17 landmarks (torso and arms)
                for i in range(17):
                    lm = results.pose_landmarks.landmark[i]
                    landmarks.extend([lm.x, lm.y])
                video_data.append(landmarks)
        
        cap.release()
        return {"label": label, "landmarks": video_data}

    def process_directory(self, dataset_dir: str):
        """Processes all videos in a directory structure (folder name as label)."""
        dataset = []
        root = Path(dataset_dir)
        
        for label_dir in root.iterdir():
            if label_dir.is_dir():
                logger.info(f"Processing class: {label_dir.name}")
                for video_file in label_dir.glob("*.mp4"):
                    data = self.extract_landmarks_from_video(str(video_file), label_dir.name)
                    if len(data["landmarks"]) >= 30: # Minimum frames for LSTM
                        dataset.append(data)
                        
        with open(self.output_path, "w") as f:
            json.dump(dataset, f)
        logger.info(f"Dataset preparation complete. Saved to {self.output_path}")

if __name__ == "__main__":
    # Example usage
    # prep = DatasetPrep()
    # prep.process_directory("training/datasets/RWF-2000")
    pass
