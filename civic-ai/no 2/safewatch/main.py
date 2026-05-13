# SafeWatch AI - Production Build v1.0.1
# Finalized and Synced to GitHub with correct author attribution.
import cv2
import yaml
import time
import threading
import signal
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from capture.stream_manager import StreamManager
from capture.frame_sampler import FrameSampler
from detection.person_detector import PersonDetector
from detection.pose_estimator import PoseEstimator
from detection.optical_flow import OpticalFlowAnalyzer
from detection.zone_manager import ZoneManager
from classifier.velocity_tracker import VelocityTracker
from classifier.skeleton_analyzer import SkeletonAnalyzer
from classifier.action_classifier import ActionClassifier
from threats.threat_engine import ThreatEngine
from database.db_manager import DatabaseManager
from database.incident_logger import IncidentLogger
from alerts.alert_manager import AlertManager

class SafeWatchSystem:
    """The main application controller for the SafeWatch CCTV system."""

    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Initialize Core Components
        self.db = DatabaseManager(self.config["database"]["path"])
        self.logger_db = IncidentLogger(self.db)
        self.alert_manager = AlertManager(self.config, self.logger_db)
        
        self.stream_manager = StreamManager()
        self.person_detector = PersonDetector(
            self.config["models"]["yolo"]["path"],
            self.config["models"]["yolo"]["confidence"]
        )
        self.pose_estimator = PoseEstimator()
        self.action_classifier = ActionClassifier(self.config["models"]["classifier"]["path"])
        
        self.running = False
        self.threads = []
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def _load_config(self, path: str):
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        log_dir = Path(self.config["system"]["log_dir"])
        log_dir.mkdir(exist_ok=True)
        logger.add(log_dir / "safewatch_{time}.log", rotation="10 MB", level="INFO")
        logger.info("SafeWatch Logging Initialized.")

    def run_camera_pipeline(self, camera_config: dict):
        """Main processing pipeline for a single camera stream."""
        cam_id = camera_config["id"]
        logger.info(f"Starting pipeline for camera: {cam_id}")
        
        self.stream_manager.add_camera(cam_id, camera_config["source"], camera_config["fps_limit"])
        stream = self.stream_manager.get_stream(cam_id)
        
        sampler = FrameSampler()
        flow_analyzer = OpticalFlowAnalyzer()
        zone_manager = ZoneManager() # Add zones from config if needed
        velocity_tracker = VelocityTracker()
        skeleton_analyzer = SkeletonAnalyzer()
        threat_engine = ThreatEngine(cam_id, self.config)
        
        # Pose and action history per person
        person_histories = {} # id -> deque of landmarks

        while self.running:
            frame = stream.read()
            if frame is None:
                time.sleep(0.01)
                continue
            
            if not sampler.should_process(frame):
                continue
            
            # 1. Detection & Tracking
            detections = self.person_detector.detect(frame)
            active_ids = [d["id"] for d in detections]
            velocity_tracker.cleanup(active_ids)
            
            # 2. Motion Analysis
            motion_data = flow_analyzer.analyze(frame)
            
            # 3. Individual Analysis
            for det in detections:
                tid = det["id"]
                # Velocity
                v_data = velocity_tracker.update(tid, ((det["bbox"][0] + det["bbox"][2])//2, det["bbox"][3]))
                det.update(v_data)
                
                # Pose
                pose_res = self.pose_estimator.estimate(frame, det["bbox"])
                det["pose_landmarks"] = pose_res["landmarks"]
                
                # Features
                features = skeleton_analyzer.extract_features(det["pose_landmarks"])
                det["pose_features"] = features
                
                # History for Action Classification
                if tid not in person_histories:
                    from collections import deque
                    person_histories[tid] = deque(maxlen=30)
                
                if det["pose_landmarks"]:
                    person_histories[tid].append(det["pose_landmarks"])
                
                # Action Classification
                if len(person_histories[tid]) == 30:
                    seq = self.action_classifier.preprocess_landmarks(list(person_histories[tid]))
                    if seq is not None:
                        action_res = self.action_classifier.predict(seq)
                        det["action"] = action_res["label"]
                
                det["pose_history"] = list(person_histories[tid])

            # 4. Zone/Trespass Check
            trespassers = zone_manager.check_trespass(detections)
            
            # 5. Threat Aggregation
            events = threat_engine.process(detections, motion_data, trespassers)
            
            # 6. Alerting
            for event in events:
                self.alert_manager.trigger(event, frame)

        logger.info(f"Pipeline for {cam_id} stopped.")

    def start(self):
        """Starts all enabled camera pipelines."""
        self.running = True
        for cam_cfg in self.config["cameras"]:
            if cam_cfg["enabled"]:
                t = threading.Thread(target=self.run_camera_pipeline, args=(cam_cfg,), daemon=True)
                t.start()
                self.threads.append(t)
        
        logger.info("SafeWatch System Started.")
        while self.running:
            time.sleep(1)

    def shutdown(self, signum=None, frame=None):
        logger.info("Shutdown signal received. Cleaning up...")
        self.running = False
        self.stream_manager.stop_all()
        self.db.close()
        sys.exit(0)

if __name__ == "__main__":
    system = SafeWatchSystem()
    system.start()
