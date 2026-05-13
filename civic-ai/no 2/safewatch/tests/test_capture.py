import pytest
import cv2
import numpy as np
import time
from safewatch.capture.camera_stream import CameraStream
from safewatch.capture.frame_sampler import FrameSampler

def test_camera_stream_initialization():
    stream = CameraStream("test_cam", 0)
    assert stream.camera_id == "test_cam"
    assert stream.source == 0
    assert stream.stopped == False

def test_frame_sampler():
    sampler = FrameSampler(motion_threshold=100, skip_interval=0)
    
    # Create two different frames
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # First frame should be processed
    assert sampler.should_process(frame1) == True
    
    # Second frame should be processed (huge motion)
    assert sampler.should_process(frame2) == True

def test_frame_sampler_skip():
    sampler = FrameSampler(skip_interval=1)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Frame 1: Index 1, 1%2 != 0 -> skip (Wait, my logic was frame_idx % (skip + 1) != 0)
    # Let's check logic: if frame_idx is 1, and skip is 1. 1 % 2 = 1. 1 != 0 is True. Returns False.
    # So every 2nd frame is processed.
    assert sampler.should_process(frame) == False
    assert sampler.should_process(frame) == True
