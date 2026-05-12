# SafeWatch Models Directory

This directory stores the AI models used by SafeWatch for detection and behavior classification.

## Required Models

| Model | Filename | Purpose |
|-------|----------|---------|
| YOLOv8 | `yolov8n.pt` | Real-time person detection (Auto-downloaded if missing) |
| Action Classifier | `action_classifier.onnx` | Behavioral classification (Fall, Fight, etc.) |

## Optional Custom Models
If you train custom models using the scripts in `training/`, place them here and update `config.yaml`.
- `custom_yolo.pt`: Optimized for specific CCTV environments.
- `action_classifier_v2.onnx`: Improved behavioral model.
