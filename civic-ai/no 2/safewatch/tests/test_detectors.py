import pytest
import numpy as np
from safewatch.threats.fight_detector import FightDetector
from safewatch.threats.fall_detector import FallDetector

def test_fight_detector_no_persons():
    detector = FightDetector()
    res = detector.detect([], {})
    assert res["detected"] == False

def test_fight_detector_proximity():
    detector = FightDetector(proximity_threshold=200)
    persons = [
        {"id": 1, "bbox": [10, 10, 50, 50], "velocity": 0.0},
        {"id": 2, "bbox": [15, 15, 55, 55], "velocity": 0.0}
    ]
    # They are very close
    res = detector.detect(persons, {})
    # fight_score += 0.3 for proximity. Needs 0.7 for True.
    assert res["confidence"] >= 0.3

def test_fall_detector_horizontal():
    detector = FallDetector()
    person = {
        "id": 1,
        "pose_features": {"is_horizontal": True, "hip_height": 0.8},
        "action": "Falling"
    }
    history = [{"hip_height": 0.5}]
    res = detector.detect(person, history)
    # is_horizontal (0.4) + drop (0.5 if > 0.15) + action (0.6) = 1.0
    assert res["detected"] == True
