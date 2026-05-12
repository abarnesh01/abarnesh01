# SafeWatch Training on Google Colab

This directory contains scripts for training the custom Action Classifier and YOLOv8 models.

## Training Instructions

1.  **Open Google Colab**: Navigate to [Google Colab](https://colab.research.google.com/).
2.  **Upload Scripts**: Upload the contents of this `training/` directory to your Colab environment.
3.  **Install Requirements**:
    ```bash
    !pip install ultralytics mediapipe onnxruntime loguru
    ```
4.  **Prepare Dataset**:
    Run `dataset_prep.py` to download and organize the required datasets (RWF-2000, UCF-Crime, etc.).
5.  **Train Classifier**:
    Run `train_classifier.py` to train the LSTM-based action recognition model.
6.  **Export to ONNX**:
    Run `export_onnx.py` to convert the trained `.pt` model to `.onnx` for high-performance CPU inference.
7.  **Download Models**:
    Download the resulting `action_classifier.onnx` and place it in the `safewatch/models/` directory on your local machine.

## Dataset Sources
- RWF-2000
- UCF-Crime
- Le2i Fall Detection
- Hockey Fight Dataset
