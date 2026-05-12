"""
SafeWatch — Action Classifier
ONNX-based action classification with rule-based fallback.
"""

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
from loguru import logger

from detection.pose_estimator import PoseResult

ACTION_CLASSES = [
    "normal", "fight", "fall", "assault", "harassment",
    "abuse", "panic", "unconscious", "other",
]


@dataclass
class ActionResult:
    """Classification result for an action."""
    action_class: str
    confidence: float
    top3_predictions: list[tuple[str, float]]

    def __repr__(self) -> str:
        return f"ActionResult(class='{self.action_class}', conf={self.confidence:.2f})"


class ActionClassifier:
    """Action classifier using ONNX model with rule-based fallback."""

    def __init__(self, model_path: str = "models/action_classifier.onnx") -> None:
        self._model_path = Path(model_path)
        self._session = None
        self._lock = threading.Lock()
        self._use_onnx = False
        self._input_name = ""
        self._output_name = ""
        self._load_model()

    def __repr__(self) -> str:
        mode = "ONNX" if self._use_onnx else "rule-based"
        return f"ActionClassifier(mode={mode})"

    def _load_model(self) -> None:
        """Load ONNX model if available, otherwise use rule-based fallback."""
        if not self._model_path.exists():
            logger.warning(
                f"ONNX model not found at {self._model_path}, "
                f"using rule-based fallback classifier"
            )
            self._use_onnx = False
            return

        try:
            import onnxruntime as ort
            self._session = ort.InferenceSession(
                str(self._model_path),
                providers=["CPUExecutionProvider"],
            )
            self._input_name = self._session.get_inputs()[0].name
            self._output_name = self._session.get_outputs()[0].name
            self._use_onnx = True
            logger.info(f"ONNX action classifier loaded from {self._model_path}")
        except Exception as e:
            logger.warning(f"Failed to load ONNX model: {e}, using rule-based fallback")
            self._use_onnx = False

    def prepare_input(self, pose_sequence: list[PoseResult]) -> np.ndarray:
        """Normalize landmark coordinates into model input format.
        
        Input: sequence of PoseResult objects (up to 30 frames).
        Output: numpy array of shape (1, 30, 99) = batch x frames x (33 landmarks * 3 coords).
        """
        seq_len = 30
        feature_dim = 99  # 33 landmarks * 3 (x, y, z)
        data = np.zeros((seq_len, feature_dim), dtype=np.float32)

        for frame_idx, pose in enumerate(pose_sequence[-seq_len:]):
            for lm_idx, lm in enumerate(pose.landmarks[:33]):
                base = lm_idx * 3
                data[frame_idx, base] = lm.x
                data[frame_idx, base + 1] = lm.y
                data[frame_idx, base + 2] = lm.z

        return data.reshape(1, seq_len, feature_dim)

    def classify(
        self,
        pose_sequence: list[PoseResult],
        skeleton_features: Optional[dict[str, Any]] = None,
    ) -> ActionResult:
        """Classify action from a sequence of poses."""
        if self._use_onnx and self._session is not None:
            return self._classify_onnx(pose_sequence)
        return self._classify_rule_based(pose_sequence, skeleton_features)

    def _classify_onnx(self, pose_sequence: list[PoseResult]) -> ActionResult:
        """Classify using ONNX model."""
        with self._lock:
            try:
                input_data = self.prepare_input(pose_sequence)
                outputs = self._session.run(
                    [self._output_name],
                    {self._input_name: input_data},
                )
                probs = outputs[0][0]

                if len(probs) != len(ACTION_CLASSES):
                    logger.warning("ONNX output size mismatch, using rule-based fallback")
                    return self._classify_rule_based(pose_sequence, None)

                top_idx = np.argmax(probs)
                sorted_indices = np.argsort(probs)[::-1]
                top3 = [
                    (ACTION_CLASSES[i], float(probs[i]))
                    for i in sorted_indices[:3]
                ]

                return ActionResult(
                    action_class=ACTION_CLASSES[top_idx],
                    confidence=float(probs[top_idx]),
                    top3_predictions=top3,
                )
            except Exception as e:
                logger.error(f"ONNX inference error: {e}")
                return self._classify_rule_based(pose_sequence, None)

    def _classify_rule_based(
        self,
        pose_sequence: list[PoseResult],
        skeleton_features: Optional[dict[str, Any]],
    ) -> ActionResult:
        """Rule-based fallback classification using skeleton angles and velocities."""
        if not pose_sequence:
            return ActionResult(
                action_class="normal",
                confidence=0.5,
                top3_predictions=[("normal", 0.5), ("other", 0.3), ("fall", 0.1)],
            )

        scores = {cls: 0.0 for cls in ACTION_CLASSES}
        scores["normal"] = 0.3

        latest = pose_sequence[-1]

        # --- Check for fall ---
        l_hip = latest.get_landmark("left_hip")
        r_hip = latest.get_landmark("right_hip")
        l_shoulder = latest.get_landmark("left_shoulder")
        r_shoulder = latest.get_landmark("right_shoulder")
        nose = latest.get_landmark("nose")

        if l_hip and r_hip and l_shoulder and r_shoulder:
            hip_y = (l_hip.y + r_hip.y) / 2.0
            shoulder_y = (l_shoulder.y + r_shoulder.y) / 2.0
            torso_height = abs(shoulder_y - hip_y)

            if torso_height < 0.04:
                scores["fall"] += 0.5
                scores["unconscious"] += 0.3

            if nose and nose.y > hip_y:
                scores["fall"] += 0.3

        # --- Check for rapid arm movement (fight/assault) ---
        if skeleton_features:
            arm_level = skeleton_features.get("arm_raise_level", 0.0)
            if arm_level is not None and arm_level > 0.7:
                scores["fight"] += 0.2
                scores["assault"] += 0.2

            lean = skeleton_features.get("body_lean_angle", 0.0)
            if lean is not None and lean > 60:
                scores["fall"] += 0.3

            orientation = skeleton_features.get("body_orientation", "standing")
            if orientation == "lying":
                scores["fall"] += 0.4
                scores["unconscious"] += 0.3

        # --- Check pose sequence for sudden changes ---
        if len(pose_sequence) >= 5:
            hip_y_values = []
            for p in pose_sequence[-10:]:
                lh = p.get_landmark("left_hip")
                rh = p.get_landmark("right_hip")
                if lh and rh:
                    hip_y_values.append((lh.y + rh.y) / 2.0)

            if len(hip_y_values) >= 3:
                hip_diff = hip_y_values[-1] - hip_y_values[0]
                if hip_diff > 0.15:
                    scores["fall"] += 0.4

        # --- Check for stillness (unconscious) ---
        if len(pose_sequence) >= 10:
            positions = []
            for p in pose_sequence[-10:]:
                lh = p.get_landmark("left_hip")
                rh = p.get_landmark("right_hip")
                if lh and rh:
                    positions.append(((lh.x + rh.x) / 2.0, (lh.y + rh.y) / 2.0))

            if len(positions) >= 5:
                total_movement = sum(
                    np.sqrt((positions[i][0] - positions[i-1][0])**2 +
                            (positions[i][1] - positions[i-1][1])**2)
                    for i in range(1, len(positions))
                )
                if total_movement < 0.01:
                    scores["unconscious"] += 0.3

        # --- Normalize and pick top ---
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        sorted_actions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_class = sorted_actions[0][0]
        top_conf = sorted_actions[0][1]
        top3 = [(cls, float(conf)) for cls, conf in sorted_actions[:3]]

        return ActionResult(
            action_class=top_class,
            confidence=float(top_conf),
            top3_predictions=top3,
        )

    @property
    def is_onnx_loaded(self) -> bool:
        return self._use_onnx
