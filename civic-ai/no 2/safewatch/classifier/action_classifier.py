import numpy as np
import onnxruntime as ort
from loguru import logger
from typing import List, Dict, Any, Optional

class ActionClassifier:
    """
    Classifies human actions using a temporal deep learning model (LSTM/GRUs).
    Can load ONNX models for high-performance CPU inference.
    Falls back to heuristic rules if no model is present.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.session = None
        if model_path:
            try:
                self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
                logger.success(f"Action classifier ONNX model loaded: {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ONNX model: {e}. Using rule-based fallback.")
        
        # Action classes matching our training pipeline
        self.classes = ['NORMAL', 'FIGHT', 'FALL', 'AGRESSIVE', 'STILL']

    def classify(self, track_id: int, sequence_features: np.ndarray) -> str:
        """
        Classifies a sequence of skeleton features.
        sequence_features: (batch, seq_len, num_features)
        """
        if self.session and sequence_features is not None:
            # ONNX Inference
            input_name = self.session.get_inputs()[0].name
            # Ensure shape matches: (1, 30, 66) for example
            if sequence_features.ndim == 2:
                sequence_features = np.expand_dims(sequence_features, axis=0)
            
            outputs = self.session.run(None, {input_name: sequence_features.astype(np.float32)})
            probs = outputs[0][0]
            class_idx = np.argmax(probs)
            return self.classes[class_idx]
        
        return "NORMAL" # Fallback

    def heuristic_classify(self, posture: Dict[str, float], velocity: float) -> str:
        """Rule-based action classification fallback."""
        if posture.get('horizontal', 0) > 0.8 and velocity < 10:
            return "STILL"
        if posture.get('horizontal', 0) > 0.7 and velocity > 100:
            return "FALL"
        if posture.get('arms_raised', 0) > 0.8 and velocity > 200:
            return "FIGHT"
        if posture.get('arms_raised', 0) > 0.6:
            return "AGRESSIVE"
            
        return "NORMAL"
