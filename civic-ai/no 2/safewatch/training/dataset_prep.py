"""
SafeWatch — Dataset Preparation (Google Colab)
Downloads and organizes open-source action recognition datasets.
"""

import csv
import os
import random
import shutil
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


class DatasetPrep:
    """Prepares and organizes datasets for action classifier training."""

    CLASSES = ["fight", "fall", "normal", "assault", "harassment",
               "abuse", "panic", "unconscious", "other"]

    DATASET_SOURCES = {
        "RWF-2000": {
            "description": "Fight detection dataset — 2000 clips",
            "url": "https://github.com/mchengny/RWF2000-Video-Database-for-Violence-Detection",
            "labels": ["fight", "normal"],
        },
        "UCF-Crime": {
            "description": "UCF Crime subset — 13 anomaly classes",
            "url": "https://www.crcv.ucf.edu/projects/real-world/",
            "labels": ["assault", "fight", "abuse", "normal"],
        },
        "Le2i-Fall": {
            "description": "Le2i Fall Detection dataset",
            "url": "http://le2i.cnrs.fr/Fall-detection-Dataset",
            "labels": ["fall", "normal"],
        },
        "Hockey-Fight": {
            "description": "Hockey Fight dataset — 1000 clips",
            "url": "https://academictorrents.com/details/38d9ed996a5a75a039b84571f6e2fa488000b3a5",
            "labels": ["fight", "normal"],
        },
    }

    def __init__(self, base_dir: str = "data") -> None:
        self._base_dir = Path(base_dir)
        self._train_dir = self._base_dir / "train"
        self._val_dir = self._base_dir / "val"
        self._manifest_path = self._base_dir / "manifest.csv"

    def __repr__(self) -> str:
        return f"DatasetPrep(base_dir='{self._base_dir}')"

    def setup_directories(self) -> None:
        """Create the directory structure for all classes."""
        for cls in self.CLASSES:
            (self._train_dir / cls).mkdir(parents=True, exist_ok=True)
            (self._val_dir / cls).mkdir(parents=True, exist_ok=True)
        print(f"Directory structure created at {self._base_dir}")

    def print_dataset_info(self) -> None:
        """Print information about available datasets."""
        print("=" * 60)
        print("SafeWatch — Available Datasets for Training")
        print("=" * 60)
        for name, info in self.DATASET_SOURCES.items():
            print(f"\n📦 {name}")
            print(f"   Description: {info['description']}")
            print(f"   URL: {info['url']}")
            print(f"   Labels: {', '.join(info['labels'])}")
        print("\n" + "=" * 60)
        print("Download datasets manually and place videos in:")
        print(f"  {self._base_dir}/raw/<dataset_name>/<class>/")
        print("=" * 60)

    def extract_frames(
        self,
        video_dir: str,
        output_dir: str,
        label: str,
        fps: int = 1,
        max_frames_per_video: int = 30,
    ) -> int:
        """Extract frames from videos at specified FPS."""
        video_path = Path(video_dir)
        out_path = Path(output_dir) / label
        out_path.mkdir(parents=True, exist_ok=True)

        total_frames = 0
        video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

        for video_file in sorted(video_path.iterdir()):
            if video_file.suffix.lower() not in video_extensions:
                continue

            cap = cv2.VideoCapture(str(video_file))
            if not cap.isOpened():
                print(f"  ⚠️ Could not open: {video_file.name}")
                continue

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            if video_fps <= 0:
                video_fps = 25.0

            frame_interval = int(video_fps / fps)
            if frame_interval < 1:
                frame_interval = 1

            frame_idx = 0
            saved = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_interval == 0 and saved < max_frames_per_video:
                    frame = cv2.resize(frame, (224, 224))
                    frame_name = f"{video_file.stem}_frame_{frame_idx:06d}.jpg"
                    cv2.imwrite(str(out_path / frame_name), frame)
                    saved += 1
                    total_frames += 1

                frame_idx += 1

            cap.release()
            print(f"  ✅ {video_file.name}: {saved} frames extracted")

        return total_frames

    def extract_pose_landmarks(
        self,
        frames_dir: str,
        output_dir: str,
    ) -> int:
        """Extract MediaPipe pose landmarks from frames and save as numpy arrays."""
        try:
            import mediapipe as mp
        except ImportError:
            print("❌ MediaPipe required. Install with: pip install mediapipe")
            return 0

        pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
        )

        frames_path = Path(frames_dir)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        count = 0
        for img_file in sorted(frames_path.glob("*.jpg")):
            image = cv2.imread(str(img_file))
            if image is None:
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                landmarks = np.array([
                    [lm.x, lm.y, lm.z]
                    for lm in results.pose_landmarks.landmark
                ])
                npy_name = img_file.stem + ".npy"
                np.save(str(out_path / npy_name), landmarks)
                count += 1

        pose.close()
        print(f"  Extracted {count} pose landmark files from {frames_dir}")
        return count

    def split_train_val(self, source_dir: str, train_ratio: float = 0.8) -> None:
        """Split frames into train/val sets (80/20)."""
        source = Path(source_dir)

        for cls_dir in source.iterdir():
            if not cls_dir.is_dir():
                continue

            cls_name = cls_dir.name
            files = list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.npy"))
            random.shuffle(files)

            split_idx = int(len(files) * train_ratio)
            train_files = files[:split_idx]
            val_files = files[split_idx:]

            train_dest = self._train_dir / cls_name
            val_dest = self._val_dir / cls_name
            train_dest.mkdir(parents=True, exist_ok=True)
            val_dest.mkdir(parents=True, exist_ok=True)

            for f in train_files:
                shutil.copy2(str(f), str(train_dest / f.name))
            for f in val_files:
                shutil.copy2(str(f), str(val_dest / f.name))

            print(f"  {cls_name}: {len(train_files)} train, {len(val_files)} val")

    def augment_data(self, frames_dir: str) -> int:
        """Augment frames with flipping, brightness, and slight rotation."""
        frames_path = Path(frames_dir)
        augmented = 0

        for img_file in list(frames_path.glob("*.jpg")):
            image = cv2.imread(str(img_file))
            if image is None:
                continue

            # Horizontal flip
            flipped = cv2.flip(image, 1)
            flip_name = img_file.stem + "_flip.jpg"
            cv2.imwrite(str(frames_path / flip_name), flipped)
            augmented += 1

            # Brightness adjustment
            bright = cv2.convertScaleAbs(image, alpha=1.2, beta=30)
            bright_name = img_file.stem + "_bright.jpg"
            cv2.imwrite(str(frames_path / bright_name), bright)
            augmented += 1

            # Slight rotation
            h, w = image.shape[:2]
            angle = random.uniform(-10, 10)
            matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            rotated = cv2.warpAffine(image, matrix, (w, h))
            rot_name = img_file.stem + "_rot.jpg"
            cv2.imwrite(str(frames_path / rot_name), rotated)
            augmented += 1

        print(f"  Generated {augmented} augmented images in {frames_dir}")
        return augmented

    def build_manifest(self) -> str:
        """Build manifest.csv with frame paths and labels."""
        rows = []

        for split_dir in [self._train_dir, self._val_dir]:
            split_name = split_dir.name
            for cls_dir in sorted(split_dir.iterdir()):
                if not cls_dir.is_dir():
                    continue
                label = cls_dir.name
                for f in sorted(cls_dir.glob("*")):
                    if f.suffix in (".jpg", ".npy"):
                        rows.append({
                            "path": str(f),
                            "label": label,
                            "split": split_name,
                        })

        with open(self._manifest_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "label", "split"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"Manifest saved: {self._manifest_path} ({len(rows)} entries)")
        return str(self._manifest_path)


if __name__ == "__main__":
    prep = DatasetPrep("data")
    prep.setup_directories()
    prep.print_dataset_info()
