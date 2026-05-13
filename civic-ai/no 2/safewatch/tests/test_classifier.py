import pytest
import numpy as np
from safewatch.classifier.velocity_tracker import VelocityTracker
from safewatch.classifier.skeleton_analyzer import SkeletonAnalyzer

def test_velocity_tracker():
    tracker = VelocityTracker()
    # Update position
    res1 = tracker.update(1, (100, 100))
    time.sleep(0.1)
    res2 = tracker.update(1, (110, 110))
    
    assert "velocity" in res2
    assert res2["velocity"] > 0

def test_skeleton_analyzer():
    analyzer = SkeletonAnalyzer()
    # Mock landmarks
    landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(33)]
    features = analyzer.extract_features(landmarks)
    
    assert "is_horizontal" in features
    assert "is_standing" in features
