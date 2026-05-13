# SafeWatch API Reference

## Capture Module

### `CameraStream`
Handles threaded frame acquisition from RTSP/USB.
- `read()`: Returns the latest frame.
- `stop()`: Terminates the thread.

### `StreamManager`
Manages multiple `CameraStream` instances.
- `add_camera(id, source)`: Registers a new camera.

## Detection Module

### `PersonDetector`
YOLOv8-based person tracker.
- `detect(frame)`: Returns list of detections with IDs and bboxes.

### `ThreatEngine`
Central aggregator for all security threats.
- `process(detections, motion, trespassers)`: Returns list of `ThreatEvent` objects.
