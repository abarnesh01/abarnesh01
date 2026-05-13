# SafeWatch AI Models

This directory stores the pre-trained and custom-trained AI models used by SafeWatch.

## Required Models

1. **YOLOv8n**: `yolov8n.pt` - used for real-time person detection and tracking.
2. **Action Classifier**: `action_classifier.onnx` - used for skeleton-based behavioral analysis.

## Model Acquisition

- YOLOv8 models are automatically downloaded by the `ultralytics` library if missing.
- Action Classifier models can be trained using the scripts in the `training/` directory.
