import pytest
from safewatch.capture.frame_sampler import FrameSampler

def test_sampler_skipping():
    sampler = FrameSampler(sample_rate=5)
    # Should process 1st, skip 2nd-5th, process 6th
    assert sampler.should_process(None) == True
    assert sampler.should_process(None) == False
    assert sampler.should_process(None) == False
    assert sampler.should_process(None) == False
    assert sampler.should_process(None) == False
    assert sampler.should_process(None) == True
