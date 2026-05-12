"""SafeWatch — Capture Module Tests."""

import time
import numpy as np


class TestCameraStream:
    """Tests for CameraStream class."""

    def test_camera_stream_creation(self):
        """Test CameraStream can be instantiated with USB and RTSP sources."""
        from capture.camera_stream import CameraStream
        stream_usb = CameraStream(source=0, camera_id="TEST-USB")
        assert stream_usb.camera_id == "TEST-USB"
        assert stream_usb.source == 0
        assert not stream_usb.is_running()
        assert not stream_usb.is_connected()

        stream_rtsp = CameraStream(
            source="rtsp://test:554/stream",
            camera_id="TEST-RTSP",
            resolution=(320, 240),
        )
        assert stream_rtsp.camera_id == "TEST-RTSP"
        assert "rtsp" in str(stream_rtsp.source)

    def test_camera_stream_repr(self):
        """Test CameraStream string representation."""
        from capture.camera_stream import CameraStream
        stream = CameraStream(source=0, camera_id="CAM-TEST")
        rep = repr(stream)
        assert "CAM-TEST" in rep
        assert "disconnected" in rep

    def test_frame_sampler_creation(self):
        """Test FrameSampler can be created with a CameraStream."""
        from capture.camera_stream import CameraStream
        from capture.frame_sampler import FrameSampler

        stream = CameraStream(source=0, camera_id="TEST")
        sampler = FrameSampler(stream, frame_skip=3, resolution=(320, 240))
        assert sampler.frame_number == 0
        sampler.update_skip_rate(10)
        assert sampler._frame_skip == 10

    def test_stream_manager_creation(self):
        """Test StreamManager initialization from config."""
        from capture.stream_manager import StreamManager

        configs = [
            {"id": "CAM-01", "source": 0, "enabled": False, "resolution": [640, 480],
             "fps_target": 15, "frame_skip": 5},
            {"id": "CAM-02", "source": "rtsp://test", "enabled": False,
             "resolution": [640, 480], "fps_target": 10, "frame_skip": 8},
        ]
        manager = StreamManager(configs)
        assert len(manager.get_all_camera_ids()) == 0  # None enabled
        status = manager.get_status()
        assert isinstance(status, dict)


if __name__ == "__main__":
    t = TestCameraStream()
    t.test_camera_stream_creation()
    print("✅ test_camera_stream_creation passed")
    t.test_camera_stream_repr()
    print("✅ test_camera_stream_repr passed")
    t.test_frame_sampler_creation()
    print("✅ test_frame_sampler_creation passed")
    t.test_stream_manager_creation()
    print("✅ test_stream_manager_creation passed")
    print("\nAll capture tests passed! ✅")
