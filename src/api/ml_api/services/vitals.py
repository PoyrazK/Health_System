from typing import Dict, Any, List
import numpy as np
import cv2
import logging
from ..processors.face_mesh import FaceMeshWrapper
from ..processors.rppg import RPPGProcessor

logger = logging.getLogger(__name__)

class VitalsService:
    """
    Service for extracting vital signs (Heart Rate) from video using rPPG.
    Refactored to match mediapipe branch implementation.
    """
    
    def __init__(self):
        # We instantiate wrappers per request or keep them if stateless enough.
        # FaceMeshWrapper is stateless regarding frame processing, but holds the MP solution.
        self.face_mesh = FaceMeshWrapper(max_num_faces=1)
        logger.info("✅ Vitals Service (rPPG) initialized")

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze a video file to extract heart rate.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30.0

        # RPPG Processor for this session
        rppg = RPPGProcessor(fps=fps, buffer_size=1000) # Larger buffer for file
        
        frame_count = 0
        rois_list = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp_ms = (frame_count / fps) * 1000.0

            # Detect Face
            results = self.face_mesh.process(frame)
            if results and results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # Get Forehead ROI (index 103, 104...) - FaceMeshWrapper has ROIs dict
                # But get_roi_average needs indices.
                # FaceMeshWrapper.ROIS['forehead']
                mean_color, _ = self.face_mesh.get_roi_average(
                    frame, results.multi_face_landmarks[0], self.face_mesh.ROIS['forehead']
                )
                
                if mean_color is not None:
                    # RPPG usually uses Green channel (index 1 in BGR)
                    green_val = mean_color[1] 
                    rppg.add_sample(green_val, timestamp_ms)

        cap.release()

        if frame_count < 30:
            return {"error": "Video too short", "heart_rate": None}

        # Calculate HR
        bpm = rppg.process()
        
        return {
            "heart_rate": float(bpm) if bpm else None,
            "frames_processed": frame_count,
            "fps": fps
        }
