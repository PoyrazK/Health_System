import cv2
import numpy as np

class SignalQuality:
    @staticmethod
    def check_brightness(frame):
        """
        Checks if the frame is too dark or too bright.
        Returns: (status_bool, message, average_brightness)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        
        if brightness < 40:
            return False, "Too Dark: Increase lighting", brightness
        if brightness > 230:
            return False, "Too Bright: Avoid direct glare", brightness
            
        return True, "Lighting Good", brightness

    @staticmethod
    def check_face_size(frame, face_landmarks):
        """
        Checks if the face is too far or too close.
        Assume face_landmarks is the bounding box or mesh.
        """
        if not face_landmarks:
             return False, "No Face Detected", 0
        
        # Simple check: Bounding box area relative to frame
        # TODO: Implement based on landmarks if passed, or just detect face rect here
        return True, "Face Found", 1.0
