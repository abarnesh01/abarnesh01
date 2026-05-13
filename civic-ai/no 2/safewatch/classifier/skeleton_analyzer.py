import numpy as np
from typing import List, Dict, Any, Tuple
import math

class SkeletonAnalyzer:
    """
    Extracts geometric features from skeletal landmarks.
    Computes angles, distances, and posture orientation.
    """
    
    # MediaPipe Pose landmark indices
    L_WRIST = 15; R_WRIST = 16
    L_ELBOW = 13; R_ELBOW = 14
    L_SHOULDER = 11; R_SHOULDER = 12
    L_HIP = 23; R_HIP = 24
    L_KNEE = 25; R_KNEE = 26
    L_ANKLE = 27; R_ANKLE = 28
    
    @staticmethod
    def calculate_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
        """Calculates angle between three points (b is vertex)."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return angle

    @staticmethod
    def get_posture_score(landmarks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyzes posture based on landmark relationships.
        Returns score for: 'horizontal', 'arms_raised', 'crouched'
        """
        if not landmarks: return {}

        # 1. Orientation (Hip to Head alignment)
        nose = landmarks[0]
        mid_hip_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
        mid_hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
        
        dx = abs(nose['x'] - mid_hip_x)
        dy = abs(nose['y'] - mid_hip_y)
        
        # Horizontal if dy < dx (roughly)
        horizontal_score = min(1.0, dx / (dy + 1e-6))
        
        # 2. Arms raised
        l_wrist_y = landmarks[15]['y']
        r_wrist_y = landmarks[16]['y']
        shoulder_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
        
        arms_raised = 0.0
        if l_wrist_y < shoulder_y: arms_raised += 0.5
        if r_wrist_y < shoulder_y: arms_raised += 0.5
        
        # 3. Crouched (Hip to Ankle height vs Shoulder height)
        mid_ankle_y = (landmarks[27]['y'] + landmarks[28]['y']) / 2
        body_height = mid_ankle_y - shoulder_y
        hip_height = mid_ankle_y - mid_hip_y
        
        crouch_score = 1.0 - (hip_height / (body_height + 1e-6))
        
        return {
            "horizontal": horizontal_score,
            "arms_raised": arms_raised,
            "crouched": max(0.0, crouch_score)
        }

    @staticmethod
    def get_joint_velocities(current_landmarks: List[Dict], prev_landmarks: List[Dict], dt: float) -> Dict[str, float]:
        """Calculates instantaneous velocity of key joints."""
        if not current_landmarks or not prev_landmarks:
            return {}
            
        velocities = {}
        key_indices = [15, 16, 0, 23, 24] # Wrists, Nose, Hips
        names = ["l_wrist", "r_wrist", "nose", "l_hip", "r_hip"]
        
        for idx, name in zip(key_indices, names):
            p1 = np.array([current_landmarks[idx]['x'], current_landmarks[idx]['y']])
            p2 = np.array([prev_landmarks[idx]['x'], prev_landmarks[idx]['y']])
            dist = np.linalg.norm(p1 - p2)
            velocities[name] = dist / dt if dt > 0 else 0
            
        return velocities
        
    @staticmethod
    def is_aggressive_posture(posture: Dict[str, float]) -> bool:
        """Heuristic for aggressive behavior based on posture."""
        return posture.get('arms_raised', 0) > 0.7 or posture.get('crouched', 0) > 0.8
