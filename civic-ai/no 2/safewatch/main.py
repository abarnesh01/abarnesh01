"""
SafeWatch — Main Entry Point
AI-Powered CCTV Threat Detection System.
"""

import argparse
import asyncio
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv
from loguru import logger

# ─── Load environment ───────────────────────
load_dotenv()

# ─── Configure logging ───────────────────────
def setup_logging(config: dict) -> None:
    """Configure loguru logging."""
    log_cfg = config.get("system", {})
    log_file = log_cfg.get("log_file", "logs/safewatch.log")
    log_level = log_cfg.get("log_level", "INFO")
    debug = log_cfg.get("debug", False)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    )
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {name}:{line} — {message}",
    )


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration."""
    path = Path(config_path)
    if not path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    logger.info(f"Configuration loaded from {config_path}")
    return config


def print_banner() -> None:
    """Print SafeWatch startup banner."""
    banner = """
╔══════════════════════════════════════════════════╗
║                                                  ║
║   ███████╗ █████╗ ███████╗███████╗               ║
║   ██╔════╝██╔══██╗██╔════╝██╔════╝               ║
║   ███████╗███████║█████╗  █████╗                  ║
║   ╚════██║██╔══██║██╔══╝  ██╔══╝                  ║
║   ███████║██║  ██║██║     ███████╗                ║
║   ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝                ║
║                                                  ║
║   ██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗    ║
║   ██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║    ║
║   ██║ █╗ ██║███████║   ██║   ██║     ███████║    ║
║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║    ║
║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║    ║
║    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝    ║
║                                                  ║
║   AI-Powered CCTV Threat Detection System        ║
║   Version 1.0.0                                  ║
║                                                  ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)


def test_cameras(config: dict) -> None:
    """Test camera connections."""
    from capture.stream_manager import StreamManager

    logger.info("Testing camera connections...")
    cameras = config.get("cameras", [])

    for cam in cameras:
        cam_id = cam["id"]
        source = cam["source"]
        enabled = cam.get("enabled", False)

        if not enabled:
            logger.info(f"[{cam_id}] Skipped (disabled)")
            continue

        logger.info(f"[{cam_id}] Testing source: {source}")

        import cv2
        cap = cv2.VideoCapture(source if isinstance(source, int) else source)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                logger.success(f"[{cam_id}] ✅ Connected — Frame: {frame.shape}")
            else:
                logger.error(f"[{cam_id}] ❌ Connected but cannot read frames")
            cap.release()
        else:
            logger.error(f"[{cam_id}] ❌ Cannot connect to {source}")

    logger.info("Camera test complete")


def test_telegram(config: dict) -> None:
    """Test Telegram bot connection."""
    from alerts.telegram_bot import SafeWatchTelegramBot

    logger.info("Testing Telegram bot connection...")
    bot = SafeWatchTelegramBot(config.get("telegram", {}))

    async def _test():
        success = await bot.test_connection()
        if success:
            logger.success("✅ Telegram bot connected successfully")
            await bot.send_system_alert("SafeWatch test alert — connection verified ✅")
        else:
            logger.error("❌ Telegram bot connection failed")

    asyncio.run(_test())


def start_dashboard(config: dict) -> Optional[subprocess.Popen]:
    """Start Streamlit dashboard in a subprocess."""
    dashboard_cfg = config.get("dashboard", {})
    host = dashboard_cfg.get("host", "0.0.0.0")
    port = dashboard_cfg.get("port", 8501)

    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    if not dashboard_path.exists():
        logger.warning("Dashboard app.py not found, skipping dashboard")
        return None

    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run",
                str(dashboard_path),
                "--server.address", host,
                "--server.port", str(port),
                "--server.headless", "true",
                "--theme.base", "dark",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(f"Dashboard started at http://{host}:{port}")
        return process
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        return None


def run_camera_pipeline(
    camera_id: str,
    config: dict,
    components: dict[str, Any],
    stop_event: threading.Event,
) -> None:
    """Run the detection pipeline for a single camera."""
    stream_manager = components["stream_manager"]
    person_detector = components["person_detector"]
    pose_estimator = components["pose_estimator"]
    optical_flow = components["optical_flow"]
    velocity_tracker = components["velocity_tracker"]
    threat_engine = components["threat_engine"]
    alert_manager = components["alert_manager"]
    db_manager = components["db_manager"]

    prev_frame = None
    frame_count = 0

    logger.info(f"[{camera_id}] Pipeline started")

    while not stop_event.is_set():
        try:
            # 1. Get frame
            frame_data = stream_manager.get_frame_data(camera_id)
            if frame_data is None:
                time.sleep(0.05)
                continue

            frame = frame_data["frame"]
            timestamp = frame_data["timestamp"]
            frame_count += 1

            # 2. Person detection
            persons = person_detector.detect(frame)

            # 3. Pose estimation
            poses = pose_estimator.estimate(frame, persons)

            # 4. Update velocity tracker
            for pose in poses:
                velocity_tracker.update(pose.person_id, pose, timestamp)

            # 5. Optical flow
            flow_result = None
            if prev_frame is not None:
                flow_result = optical_flow.analyze(prev_frame, frame)
            prev_frame = frame.copy()

            # 6. Feed to threat engine
            analysis_data = {
                "frame": frame,
                "camera_id": camera_id,
                "timestamp": timestamp,
                "persons": persons,
                "poses": poses,
                "flow_result": flow_result,
                "velocity_tracker": velocity_tracker,
                "config": config,
            }

            threat_report = threat_engine.analyze(analysis_data)

            # 7. Process threats
            if threat_report.threats_detected:
                alert_manager.process_threat_report(threat_report, frame)

            # 8. Update camera status
            if frame_count % 30 == 0:
                stream = stream_manager.get_stream(camera_id)
                fps = stream.get_fps() if stream else 0.0
                db_manager.update_camera_status(camera_id, {
                    "status": "online",
                    "fps": fps,
                    "frames_processed": frame_count,
                    "threats_today": len(threat_report.threats_detected),
                })

        except Exception as e:
            logger.error(f"[{camera_id}] Pipeline error: {e}")
            time.sleep(0.1)

    logger.info(f"[{camera_id}] Pipeline stopped")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SafeWatch — AI-Powered CCTV Threat Detection")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--dashboard-only", action="store_true", help="Start only the dashboard")
    parser.add_argument("--test-cameras", action="store_true", help="Test camera connections")
    parser.add_argument("--test-telegram", action="store_true", help="Test Telegram bot connection")
    args = parser.parse_args()

    print_banner()

    # Load config
    config = load_config(args.config)
    setup_logging(config)

    logger.info(f"SafeWatch v{config.get('system', {}).get('version', '1.0.0')} starting...")
    logger.info(f"Python {sys.version}")

    # Handle test modes
    if args.test_cameras:
        test_cameras(config)
        return

    if args.test_telegram:
        test_telegram(config)
        return

    if args.dashboard_only:
        logger.info("Starting dashboard only mode...")
        process = start_dashboard(config)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
        return

    # ─── Initialize all components ───────────────────
    logger.info("Initializing components...")

    # 1. Database
    from database.db_manager import DatabaseManager
    from database.incident_logger import IncidentLogger
    db_manager = DatabaseManager(config.get("database", {}).get("path", "logs/safewatch.db"))
    incident_logger = IncidentLogger(db_manager)
    logger.info("✅ Database initialized")

    # 2. Stream Manager
    from capture.stream_manager import StreamManager
    stream_manager = StreamManager(config.get("cameras", []))
    stream_manager.start_all()
    logger.info("✅ Stream Manager started")

    # 3. Person Detector
    from detection.person_detector import PersonDetector
    detection_cfg = config.get("detection", {})
    person_detector = PersonDetector(
        model_path=detection_cfg.get("yolo_model", "models/yolov8n.pt"),
        confidence=detection_cfg.get("yolo_confidence", 0.5),
        classes=detection_cfg.get("yolo_classes", [0]),
        max_tracked=detection_cfg.get("max_persons_tracked", 10),
    )
    logger.info("✅ Person Detector loaded")

    # 4. Pose Estimator
    from detection.pose_estimator import PoseEstimator
    pose_estimator = PoseEstimator(
        model_complexity=detection_cfg.get("pose_model_complexity", 0),
        min_confidence=detection_cfg.get("pose_min_confidence", 0.5),
    )
    logger.info("✅ Pose Estimator loaded")

    # 5. Optical Flow
    from detection.optical_flow import OpticalFlowAnalyzer
    optical_flow = OpticalFlowAnalyzer()
    logger.info("✅ Optical Flow Analyzer initialized")

    # 6. Zone Manager
    from detection.zone_manager import ZoneManager
    zone_manager = ZoneManager(args.config)
    logger.info("✅ Zone Manager initialized")

    # 7. Velocity Tracker
    from classifier.velocity_tracker import VelocityTracker
    velocity_tracker = VelocityTracker()
    logger.info("✅ Velocity Tracker initialized")

    # 8. Action Classifier
    from classifier.action_classifier import ActionClassifier
    models_cfg = config.get("models", {})
    action_classifier = ActionClassifier(
        model_path=models_cfg.get("action_classifier", "models/action_classifier.onnx"),
    )
    logger.info(f"✅ Action Classifier loaded ({action_classifier})")

    # 9. Threat Engine
    from threats.threat_engine import ThreatEngine
    threat_engine = ThreatEngine(config, zone_manager)
    logger.info("✅ Threat Engine initialized")

    # 10. Telegram Bot
    from alerts.telegram_bot import SafeWatchTelegramBot
    telegram_bot = SafeWatchTelegramBot(config.get("telegram", {}))
    logger.info(f"✅ Telegram Bot initialized ({telegram_bot})")

    # 11. Alert Manager
    from alerts.alert_manager import AlertManager
    alert_manager = AlertManager(telegram_bot, incident_logger, config)
    logger.info("✅ Alert Manager initialized")

    # Log startup to DB
    db_manager.log_system_event("INFO", "SafeWatch system started")

    # ─── Start dashboard ───────────────────
    dashboard_process = start_dashboard(config)

    # ─── Start camera pipelines ───────────────────
    stop_event = threading.Event()
    pipeline_threads: list[threading.Thread] = []

    components = {
        "stream_manager": stream_manager,
        "person_detector": person_detector,
        "pose_estimator": pose_estimator,
        "optical_flow": optical_flow,
        "velocity_tracker": velocity_tracker,
        "threat_engine": threat_engine,
        "alert_manager": alert_manager,
        "db_manager": db_manager,
    }

    for camera_id in stream_manager.get_all_camera_ids():
        thread = threading.Thread(
            target=run_camera_pipeline,
            args=(camera_id, config, components, stop_event),
            daemon=True,
            name=f"pipeline-{camera_id}",
        )
        thread.start()
        pipeline_threads.append(thread)
        logger.info(f"Pipeline thread started for {camera_id}")

    logger.info(f"🚀 SafeWatch running with {len(pipeline_threads)} camera pipeline(s)")
    logger.info(f"📊 Dashboard: http://localhost:{config.get('dashboard', {}).get('port', 8501)}")

    # ─── Graceful shutdown ───────────────────
    def shutdown_handler(signum, frame):
        logger.info("Shutdown signal received...")
        stop_event.set()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Ctrl+C received, shutting down...")
        stop_event.set()

    # Cleanup
    logger.info("Stopping all components...")
    stream_manager.stop_all()
    threat_engine.shutdown()
    pose_estimator.close()

    if dashboard_process:
        dashboard_process.terminate()

    db_manager.log_system_event("INFO", "SafeWatch system stopped")
    logger.info("SafeWatch stopped. Goodbye! 👋")


if __name__ == "__main__":
    main()
