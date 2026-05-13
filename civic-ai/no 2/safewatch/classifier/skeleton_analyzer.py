import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger

class SkeletonAnalyzer:
    """Analyzes MediaPipe skeleton landmarks for postural features."""

    def __init__(self):
        # Indices for key joints in MediaPipe Pose
        self.joints = {
            "nose": 0, "l_shoulder": 11, "r_shoulder": 12,
            "l_elbow": 13, "r_elbow": 14, "l_wrist": 15, "r_wrist": 16,
            "l_hip": 23, "r_hip": 24, "l_knee": 25, "r_knee": 26,
            "l_ankle": 27, "r_ankle": 28
        }

    def extract_features(self, landmarks: List[Dict]) -> Dict[str, Any]:
        """Extracts high-level postural features like torso angle, arm extension, etc."""
        if not landmarks:
            return {}

        try:
            # Torso inclination (average of shoulders to average of hips)
            l_sh = np.array([landmarks[11]['x'], landmarks[11]['y']])
            r_sh = np.array([landmarks[12]['x'], landmarks[12]['y']])
            l_hip = np.array([landmarks[23]['x'], landmarks[23]['y']])
            r_hip = np.array([landmarks[24]['x'], landmarks[24]['y']])
            
            mid_shoulder = (l_sh + r_sh) / 2
            mid_hip = (l_hip + r_hip) / 2
            
            # Vertical reference
            torso_vec = mid_shoulder - mid_hip
            vertical_vec = np.array([0, -1])
            
            # Torso angle relative to vertical (0 = standing straight, 90 = horizontal)
            cos_theta = np.dot(torso_vec, vertical_vec) / (np.linalg.norm(torso_vec) * np.linalg.norm(vertical_vec) + 1e-6)
            torso_angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))

            # Arm raised height (relative to shoulders)
            l_wrist_y = landmarks[15]['y']
            r_wrist_y = landmarks[16]['y']
            shoulder_y = mid_shoulder[1]
            
            l_arm_raised = shoulder_y - l_wrist_y > 0.1 # Threshold for raised arm
            r_arm_raised = shoulder_y - r_wrist_y > 0.1

            # Proximity of wrists (clashing/fighting indicator)
            wrist_dist = np.linalg.norm(np.array([landmarks[15]['x'], landmarks[15]['y']]) - 
                                        np.array([landmarks[16]['x'], landmarks[16]['y']]))

            return {
                "torso_angle": float(torso_angle),
                "l_arm_raised": bool(l_arm_raised),
                "r_arm_raised": bool(r_arm_raised),
                "wrist_dist": float(wrist_dist),
                "is_horizontal": torso_angle > 60.0,
                "hip_height": float(mid_hip[1])
            }
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}

    def is_falling(self, history: List[Dict[str, Any]]) -> bool:
        """Analyzes a short history of skeleton features to detect a fall."""
        if len(history) < 5:
            return False
            
        # Fall characteristic: Rapid decrease in hip height followed by horizontal orientation
        start_hip = history[0].get("hip_height", 0)
        end_hip = history[-1].get("hip_height", 0)
        
        # In normalized coordinates, Y increases downwards. 
        # So a fall means hip_height increases significantly in a short time.
        hip_drop = end_hip - start_hip
        is_horizontal = history[-1].get("is_horizontal", False)
        
        if hip_drop > 0.15 and is_horizontal:
            return True
        return False
