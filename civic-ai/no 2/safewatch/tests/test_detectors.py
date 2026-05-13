import unittest
from threats.fall_detector import FallDetector
from threats.fight_detector import FightDetector

class TestDetectors(unittest.TestCase):
    def test_fall_detector_init(self):
        detector = FallDetector()
        self.assertIsNotNone(detector)

    def test_fight_detector_init(self):
        detector = FightDetector()
        self.assertIsNotNone(detector)

if __name__ == "__main__":
    unittest.main()
