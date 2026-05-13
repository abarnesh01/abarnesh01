import onnxruntime as ort
import numpy as np
from loguru import logger
from typing import List, Optional

class ActionClassifier:
    """LSTM-based action classifier running on ONNX Runtime."""

    def __init__(self, model_path: str = "models/action_classifier.onnx"):
        self.model_path = model_path
        self.session: Optional[ort.InferenceSession] = None
        self.classes = ["Standing", "Walking", "Running", "Falling", "Fighting", "Kicking", "Punching"]
        
        try:
            self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            logger.info(f"Action Classifier loaded: {model_path}")
        except Exception as e:
            logger.warning(f"Failed to load ONNX model {model_path}: {e}. Fallback to rule-based detection.")

    def predict(self, sequence: np.ndarray) -> dict:
        """
        Predicts action from a sequence of skeleton landmarks.
        sequence shape: (1, 30, 34) -> (batch, frames, keypoints*2)
        """
        if self.session is None:
            return {"label": "Unknown", "confidence": 0.0}

        try:
            # Prepare input
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: sequence.astype(np.float32)})
            
            # Softmax/Argmax
            probs = outputs[0][0]
            idx = np.argmax(probs)
            
            return {
                "label": self.classes[idx] if idx < len(self.classes) else "Unknown",
                "confidence": float(probs[idx]),
                "all_probs": {self.classes[i]: float(probs[i]) for i in range(len(self.classes))}
            }
        except Exception as e:
            logger.error(f"Classification inference failed: {e}")
            return {"label": "Error", "confidence": 0.0}

    def preprocess_landmarks(self, landmarks_history: List[List[dict]]) -> Optional[np.ndarray]:
        """Converts landmark history to the expected ONNX input shape."""
        # Need exactly 30 frames for the sequence
        if len(landmarks_history) < 30:
            return None
            
        # Select 17 key landmarks (subset of 33 for efficiency)
        # We'll use 0-16 for basic torso/arm analysis
        seq = []
        for frame_landmarks in landmarks_history[-30:]:
            frame_vec = []
            for i in range(17):
                frame_vec.extend([frame_landmarks[i]['x'], frame_landmarks[i]['y']])
            seq.append(frame_vec)
            
        return np.array(seq).reshape(1, 30, 34)
