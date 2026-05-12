"""SafeWatch — Detection & Threat Module Tests."""

import numpy as np


class TestDetectors:
    """Tests for detection and threat modules."""

    def test_person_detector_creation(self):
        """Test PersonDetector can be instantiated."""
        from detection.person_detector import PersonDetector, Person
        detector = PersonDetector(
            model_path="models/yolov8n.pt",
            confidence=0.5,
        )
        assert repr(detector) is not None

        # Test Person dataclass
        person = Person(
            id=1, bbox=(100, 100, 200, 300),
            confidence=0.95, center=(150, 200),
            area=20000, width=100, height=200,
        )
        assert person.id == 1
        assert person.confidence == 0.95
        assert "Person" in repr(person)

    def test_skeleton_analyzer(self):
        """Test SkeletonAnalyzer methods with mock pose data."""
        from classifier.skeleton_analyzer import SkeletonAnalyzer
        from detection.pose_estimator import PoseResult, Landmark

        analyzer = SkeletonAnalyzer()

        # Create a standing person pose
        landmarks = [Landmark(x=0.5, y=0.1 + i * 0.025, z=0.0, visibility=0.9) for i in range(33)]

        # Override key joints for standing
        landmarks[11] = Landmark(x=0.45, y=0.3, z=0.0, visibility=0.9)  # left_shoulder
        landmarks[12] = Landmark(x=0.55, y=0.3, z=0.0, visibility=0.9)  # right_shoulder
        landmarks[23] = Landmark(x=0.45, y=0.55, z=0.0, visibility=0.9)  # left_hip
        landmarks[24] = Landmark(x=0.55, y=0.55, z=0.0, visibility=0.9)  # right_hip
        landmarks[25] = Landmark(x=0.45, y=0.75, z=0.0, visibility=0.9)  # left_knee
        landmarks[26] = Landmark(x=0.55, y=0.75, z=0.0, visibility=0.9)  # right_knee
        landmarks[0] = Landmark(x=0.5, y=0.1, z=0.0, visibility=0.9)    # nose

        from detection.pose_estimator import KEYPOINT_NAMES
        keypoints = {}
        for idx, name in enumerate(KEYPOINT_NAMES):
            if idx < len(landmarks):
                keypoints[name] = landmarks[idx]

        pose = PoseResult(
            person_id=1,
            landmarks=landmarks,
            keypoints=keypoints,
            bbox=(100, 50, 300, 400),
            confidence=0.9,
        )

        orientation = analyzer.get_body_orientation(pose)
        assert orientation in ("standing", "sitting", "lying", "crouching", None)

        lean = analyzer.get_body_lean_angle(pose)
        assert lean is None or isinstance(lean, float)

        com = analyzer.get_center_of_mass(pose)
        assert com is not None
        assert len(com) == 2

        horizontal = analyzer.is_person_horizontal(pose)
        assert isinstance(horizontal, bool)

    def test_velocity_tracker(self):
        """Test VelocityTracker update and query methods."""
        from classifier.velocity_tracker import VelocityTracker
        from detection.pose_estimator import PoseResult, Landmark, KEYPOINT_NAMES

        tracker = VelocityTracker(max_history=60)

        # Create two pose frames with movement
        def make_pose(x_offset: float) -> PoseResult:
            landmarks = [Landmark(x=0.5 + x_offset, y=0.5, z=0.0, visibility=0.9) for _ in range(33)]
            keypoints = {}
            for idx, name in enumerate(KEYPOINT_NAMES):
                if idx < len(landmarks):
                    keypoints[name] = landmarks[idx]
            return PoseResult(person_id=1, landmarks=landmarks, keypoints=keypoints,
                            bbox=(100, 100, 200, 300), confidence=0.9)

        pose1 = make_pose(0.0)
        pose2 = make_pose(0.1)

        tracker.update(1, pose1, 0.0)
        tracker.update(1, pose2, 0.1)

        vel = tracker.get_velocity(1, "nose")
        assert vel >= 0.0

        accel = tracker.get_acceleration(1, "nose")
        assert isinstance(accel, float)

        unknown_vel = tracker.get_velocity(999, "nose")
        assert unknown_vel == 0.0

        trajectory = tracker.get_trajectory(1, 5)
        assert isinstance(trajectory, list)

    def test_fight_detector(self):
        """Test FightDetector returns empty list with insufficient persons."""
        from threats.fight_detector import FightDetector
        from classifier.velocity_tracker import VelocityTracker

        detector = FightDetector({
            "confidence_threshold": 0.82,
            "min_persons": 2,
            "velocity_threshold": 45.0,
        })

        tracker = VelocityTracker()
        # With 0 persons — should return empty
        threats = detector.detect([], [], tracker, {})
        assert threats == []
        assert isinstance(threats, list)

    def test_fall_detector_states(self):
        """Test FallDetector state machine."""
        from threats.fall_detector import FallDetector

        detector = FallDetector({
            "confidence_threshold": 0.78,
            "hip_drop_threshold": 80,
            "stillness_frames": 30,
        })

        state = detector.get_person_state(999)
        assert state == FallDetector.STANDING

    def test_threat_engine_empty(self):
        """Test ThreatEngine with no persons."""
        from threats.threat_engine import ThreatEngine, ThreatReport
        from detection.zone_manager import ZoneManager
        import numpy as np

        zone_manager = ZoneManager()
        engine = ThreatEngine({"threats": {}}, zone_manager)

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        from classifier.velocity_tracker import VelocityTracker
        vt = VelocityTracker()

        report = engine.analyze({
            "frame": frame,
            "camera_id": "TEST",
            "timestamp": 0.0,
            "persons": [],
            "poses": [],
            "flow_result": None,
            "velocity_tracker": vt,
            "config": {},
        })

        assert isinstance(report, ThreatReport)
        assert report.overall_risk_level == "SAFE"
        assert len(report.threats_detected) == 0

        engine.shutdown()


if __name__ == "__main__":
    t = TestDetectors()
    t.test_person_detector_creation()
    print("✅ test_person_detector_creation passed")
    t.test_skeleton_analyzer()
    print("✅ test_skeleton_analyzer passed")
    t.test_velocity_tracker()
    print("✅ test_velocity_tracker passed")
    t.test_fight_detector()
    print("✅ test_fight_detector passed")
    t.test_fall_detector_states()
    print("✅ test_fall_detector_states passed")
    t.test_threat_engine_empty()
    print("✅ test_threat_engine_empty passed")
    print("\nAll detector tests passed! ✅")
