import numpy as np
import math

class FaceGeometry:
    def __init__(self):
        # MediaPipe Iris Indices
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        self.LEFT_PUPIL_CENTER = 468
        self.RIGHT_PUPIL_CENTER = 473
        
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380] # EAR indices
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]

    def check_head_pose(self, landmarks):
        """
        Estimates if the user is looking at the camera.
        Uses relative distance of nose to ears/cheeks.
        """
        # Indices
        NOSE_TIP = 1
        LEFT_EAR = 234
        RIGHT_EAR = 454
        
        nose = landmarks.landmark[NOSE_TIP]
        l_ear = landmarks.landmark[LEFT_EAR]
        r_ear = landmarks.landmark[RIGHT_EAR]
        
        # Calculate distances from nose to ears
        dist_l_ear = abs(nose.x - l_ear.x)
        dist_r_ear = abs(nose.x - r_ear.x)
        
        # Avoid division by zero
        if dist_r_ear == 0: dist_r_ear = 0.001
        
        # Yaw Ratio: 1.0 is center. <0.5 or >2.0 is turning away.
        yaw_ratio = dist_l_ear / dist_r_ear
        
        if yaw_ratio < 0.3 or yaw_ratio > 3.0:
            return False, f"TURN HEAD ({yaw_ratio:.1f})"
            
        return True, "Looking Forward"

    def _euclidean_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def calculate_ear(self, landmarks, eye_indices):
        """
        Calculates Eye Aspect Ratio (EAR) to detect drowsiness/blinking.
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        # Specific to the 6 points defined in self.LEFT_EYE/RIGHT_EYE
        # P1, P4 are corners (indices 0 and 3 in the subset list)
        # P2, P6 are top/bottom pair 1 (indices 1 and 5)
        # P3, P5 are top/bottom pair 2 (indices 2 and 4)
        
        # Mapping indices from the subset list:
        # P1: eye_indices[0]
        # P2: eye_indices[1]
        # P3: eye_indices[2]
        # P4: eye_indices[3]
        # P5: eye_indices[4]
        # P6: eye_indices[5]
        
        p1 = landmarks.landmark[eye_indices[0]]
        p2 = landmarks.landmark[eye_indices[1]]
        p3 = landmarks.landmark[eye_indices[2]]
        p4 = landmarks.landmark[eye_indices[3]]
        p5 = landmarks.landmark[eye_indices[4]]
        p6 = landmarks.landmark[eye_indices[5]]
        
        vertical_1 = self._euclidean_distance(p2, p6)
        vertical_2 = self._euclidean_distance(p3, p5)
        horizontal = self._euclidean_distance(p1, p4)
        
        if horizontal == 0:
            return 0
            
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear

    def calculate_iris_diameter(self, landmarks, frame_width, frame_height):
        """
        Calculates average iris diameter in pixels.
        Note: This is relative to camera distance.
        """
        # Just take one iris for now
        p1 = landmarks.landmark[self.LEFT_IRIS[0]]
        p3 = landmarks.landmark[self.LEFT_IRIS[2]]
        
        # Convert to pixels
        dist = math.sqrt(
            ((p1.x - p3.x) * frame_width)**2 + 
            ((p1.y - p3.y) * frame_height)**2
        )
        return dist

    def check_asymmetry(self, landmarks):
        """
        Checks for Smile/Stroke asymmetry.
        Compares distance of mouth corners to nose tip.
        """
        NOSE_TIP = 1
        MOUTH_LEFT = 61
        MOUTH_RIGHT = 291
        
        nose = landmarks.landmark[NOSE_TIP]
        left = landmarks.landmark[MOUTH_LEFT]
        right = landmarks.landmark[MOUTH_RIGHT]
        
        dist_l = self._euclidean_distance(nose, left)
        dist_r = self._euclidean_distance(nose, right)
        
        # Avoid division by zero
        if dist_r == 0: dist_r = 0.001
            
        ratio = dist_l / dist_r
        
        # Asymmetry score: 0 is perfect symmetry (log ratio 0), higher is worse
        # Simple difference ratio
        asymmetry_score = abs(1.0 - ratio)
        
        return asymmetry_score, "Warning" if asymmetry_score > 0.2 else "Normal"
