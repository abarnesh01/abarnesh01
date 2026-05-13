import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from loguru import logger
from tqdm import tqdm

class DatasetPrep:
    """
    Prepares skeleton landmark datasets from video files for training the Action Classifier.
    Extracts temporal sequences of landmarks.
    """
    def __init__(self, seq_length: int = 30):
        self.seq_length = seq_length
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1)

    def extract_landmarks_from_video(self, video_path: str, label: str):
        """
        Processes a video and returns a list of sequences.
        Each sequence is (seq_length, 33*2) landmarks.
        """
        cap = cv2.VideoCapture(video_path)
        sequence = []
        data = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y]) # We use X and Y only for simplicity
                
                sequence.append(landmarks)
                
                if len(sequence) == self.seq_length:
                    data.append({
                        "sequence": np.array(sequence).flatten().tolist(),
                        "label": label
                    })
                    sequence = [] # Reset for next segment or use sliding window
                    
        cap.release()
        return data

    def process_directory(self, base_dir: str, output_csv: str):
        """
        Recursively processes videos in subdirectories (where subdir name is the label).
        """
        all_data = []
        for label in os.listdir(base_dir):
            label_dir = os.path.join(base_dir, label)
            if not os.path.isdir(label_dir): continue
            
            logger.info(f"Processing class: {label}")
            for video_file in tqdm(os.listdir(label_dir)):
                video_path = os.path.join(label_dir, video_file)
                if video_file.endswith(('.mp4', '.avi', '.mov')):
                    video_data = self.extract_landmarks_from_video(video_path, label)
                    all_data.extend(video_data)
        
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv, index=False)
        logger.success(f"Dataset saved to {output_csv}. Total samples: {len(all_data)}")

if __name__ == "__main__":
    # Example usage for Colab
    prep = DatasetPrep(seq_length=30)
    # prep.process_directory("data/raw_videos", "data/skeleton_dataset.csv")
