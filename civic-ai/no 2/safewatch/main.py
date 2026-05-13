import cv2
import yaml
import time
import signal
import sys
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Import SafeWatch Modules
from capture.stream_manager import StreamManager
from capture.frame_sampler import FrameSampler
from detection.person_detector import PersonDetector
from detection.pose_estimator import PoseEstimator
from detection.optical_flow import OpticalFlowAnalyzer
from detection.zone_manager import ZoneManager
from classifier.velocity_tracker import VelocityTracker
from threats.threat_engine import ThreatEngine
from alerts.alert_manager import AlertManager
from alerts.snapshot_builder import SnapshotBuilder
from database.db_manager import DatabaseManager

class SafeWatchApp:
    """
    Main Application class for SafeWatch CCTV Intelligence System.
    Orchestrates the real-time processing pipeline.
    """
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self._setup_logging()
        self.config = self._load_config(config_path)
        
        # Initialize Core Components
        self.db = DatabaseManager(self.config['database']['path'])
        self.stream_manager = StreamManager(self.config['cameras'])
        self.sampler = FrameSampler(sampling_rate=2)
        
        # Detection Engines
        self.detector = PersonDetector(model_path=self.config['inference']['yolo_model'])
        self.pose_engine = PoseEstimator()
        self.flow_analyzer = OpticalFlowAnalyzer()
        self.zone_manager = ZoneManager()
        
        # Intelligence & Tracking
        self.velocity_tracker = VelocityTracker()
        self.threat_engine = ThreatEngine(self.config)
        
        # Alerts
        self.alert_manager = AlertManager()
        self.snapshot_builder = SnapshotBuilder()
        
        self.running = False
        self._setup_signals()

    def _setup_logging(self):
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        logger.add("logs/safewatch.log", rotation="10 MB", level="DEBUG")
        logger.info("SafeWatch Systems Initializing...")

    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_signals(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def start(self):
        """Starts the surveillance pipeline."""
        logger.success("SafeWatch Intelligence Core Online.")
        self.running = True
        self.stream_manager.start_all()
        
        try:
            self.run_loop()
        except Exception as e:
            logger.critical(f"Pipeline crashed: {e}")
            self.stop()

    def run_loop(self):
        """Main processing loop for all active streams."""
        while self.running:
            active_streams = self.stream_manager.get_active_streams()
            
            for stream in active_streams:
                frame = stream.read()
                if frame is None: continue
                
                # 1. Smart Sampling
                if not self.sampler.should_process(frame):
                    continue
                
                # 2. Person Detection & Tracking
                detections = self.detector.detect(frame)
                self.velocity_tracker.update(detections)
                
                # 3. Pose Estimation (per person)
                poses = self.pose_engine.estimate(frame, detections)
                
                # 4. Motion Analysis (Optical Flow)
                mag, ang = self.flow_analyzer.compute_flow(frame)
                panic_score = self.flow_analyzer.analyze_panic(mag)
                
                # 5. Zone Analysis
                zone_activity = self.zone_manager.check_detections(detections)
                
                # 6. Velocity extraction for threat engine
                velocities = {det['id']: self.velocity_tracker.get_velocity(det['id']) 
                              for det in detections if det['id'] != -1}
                
                # 7. Threat Intelligence Aggregation
                threats = self.threat_engine.analyze(
                    camera_id=stream.camera_id,
                    detections=detections,
                    poses=poses,
                    velocities=velocities,
                    zone_activity=zone_activity,
                    panic_score=panic_score
                )
                
                # 8. Alert Dispatching
                for threat in threats:
                    snapshot_path = self.snapshot_builder.build(frame, threat, stream.name)
                    self.alert_manager.process_threat(threat, stream.camera_id, stream.name, snapshot_path)
                
                # 9. Optional Local Visualization (for debugging)
                if os.getenv("SHOW_PREVIEW") == "1":
                    annotated_frame = self.detector.draw_detections(frame.copy(), detections)
                    annotated_frame = self.pose_engine.draw_poses(annotated_frame, poses)
                    annotated_frame = self.threat_engine.draw_overlays(annotated_frame, threats)
                    cv2.imshow(f"SafeWatch Monitor: {stream.name}", annotated_frame)
                    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Yield CPU
            time.sleep(0.01)

    def stop(self, *args):
        """Graceful shutdown of all subsystems."""
        logger.info("SafeWatch shutting down...")
        self.running = False
        self.stream_manager.stop_all()
        cv2.destroyAllWindows()
        sys.exit(0)

if __name__ == "__main__":
    app = SafeWatchApp()
    app.start()
