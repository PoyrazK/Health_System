import cv2
import mediapipe as mp
import numpy as np

class FaceMeshWrapper:
    def __init__(self, max_num_faces=1, refine_landmarks=True):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Landmark indices (approximate for MP 468/478 detection)
        # Forehead (approximate center region)
        self.ROIS = {
            'forehead': [103, 104, 105, 69, 68, 67, 109, 10], 
            'left_cheek': [330, 347, 348, 349, 350, 266],
            'right_cheek': [101, 118, 119, 120, 121, 36]
        }
    
    def process(self, frame):
        """
        Process the frame to detect face landmarks.
        Returns: (results, frame_rgb, landmarks_list)
        """
        # MediaPipe needs RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False # Improve perf
        results = self.face_mesh.process(frame_rgb)
        frame_rgb.flags.writeable = True
        
        return results

    def get_roi_average(self, frame, landmarks, roi_indices):
        """
        Extracts the average color of a Region of Interest (ROI) defined by landmark indices.
        """
        if not landmarks:
            return None
        
        h, w, _ = frame.shape
        # Convert specific landmarks to pixel coordinates
        roi_points = []
        for idx in roi_indices:
            lm = landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            roi_points.append([x, y])
        
        roi_points = np.array(roi_points, dtype=np.int32)
        
        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(mask, roi_points, 255)
        
        # Calculate mean color in the ROI
        mean_color = cv2.mean(frame, mask=mask)[:3] # (B, G, R)
        return mean_color, roi_points
