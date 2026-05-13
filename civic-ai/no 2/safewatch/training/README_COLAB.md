# SafeWatch Training on Google Colab

This directory contains scripts for training the custom Action Classifier and YOLOv8 models.

## Training Instructions

1. **Open Google Colab**: Navigate to [Google Colab](https://colab.research.google.com/).
2. **Upload Scripts**: Upload `dataset_prep.py`, `train_classifier.py`, and `export_onnx.py`.
3. **Download Datasets**:
   - RWF-2000 for fight detection.
   - Le2i for fall detection.
4. **Run Pipeline**:
   - Run `dataset_prep.py` to extract landmarks.
   - Run `train_classifier.py` to train the LSTM.
   - Run `export_onnx.py` to convert to ONNX.

## Performance Requirements

- Use a GPU runtime for faster training.
- LSTM training can be done on CPU if the dataset is small.
