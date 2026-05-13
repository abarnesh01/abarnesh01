import unittest
from capture.camera_stream import CameraStream
import time

class TestCapture(unittest.TestCase):
    def test_camera_initialization(self):
        # Test with a dummy source (non-existent file)
        stream = CameraStream(0, "TestCam", "non_existent.mp4")
        self.assertEqual(stream.name, "TestCam")
        self.assertFalse(stream.connected)

if __name__ == "__main__":
    unittest.main()
