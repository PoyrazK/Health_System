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
        Analyze a video file to extract heart rate, SpO2, asymmetry, and triage risk.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30.0

        # RPPG Processors
        rppg_green = RPPGProcessor(fps=fps, buffer_size=1000)
        rppg_red = RPPGProcessor(fps=fps, buffer_size=1000)
        
        frame_count = 0
        face_detected_count = 0
        asymmetry_scores = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp_ms = (frame_count / fps) * 1000.0

            # Detect Face
            results = self.face_mesh.process(frame)
            if results and results.multi_face_landmarks:
                face_detected_count += 1
                landmarks = results.multi_face_landmarks[0]
                
                # 1. rPPG Signal (Forehead)
                mean_color, _ = self.face_mesh.get_roi_average(
                    frame, landmarks, self.face_mesh.ROIS['forehead']
                )
                
                if mean_color is not None:
                    # mean_color is (B, G, R)
                    rppg_green.add_sample(mean_color[1], timestamp_ms)
                    rppg_red.add_sample(mean_color[2], timestamp_ms)

                # 2. Facial Asymmetry (Simple Distance check)
                # Compare eye-to-corner-mouth or eye-to-nose distances
                # MP indices: Left Eye (33), Right Eye (263), Mouth Left (61), Mouth Right (291)
                l_eye = landmarks.landmark[33]
                r_eye = landmarks.landmark[263]
                l_mouth = landmarks.landmark[61]
                r_mouth = landmarks.landmark[291]
                
                dist_l = np.sqrt((l_eye.x - l_mouth.x)**2 + (l_eye.y - l_mouth.y)**2)
                dist_r = np.sqrt((r_eye.x - r_mouth.x)**2 + (r_eye.y - r_mouth.y)**2)
                
                asym = abs(dist_l - dist_r) / max(dist_l, dist_r) if max(dist_l, dist_r) > 0 else 0
                asymmetry_scores.append(asym)

        cap.release()

        if frame_count < 30:
            return {"error": "Video too short", "heart_rate": None}

        # Calculate BPM & SNR
        bpm = rppg_green.process()
        snr = rppg_green.last_snr
        
        # Calculate SpO2 Estimate (AC/DC Ratio of Red vs Green)
        spo2 = 98.0 # Default
        if len(rppg_red.raw_signal) > 30:
            # Simple SpO2 estimation using Red/Green ratio
            red_ac = np.std(rppg_red.raw_signal)
            red_dc = np.mean(rppg_red.raw_signal)
            green_ac = np.std(rppg_green.raw_signal)
            green_dc = np.mean(rppg_green.raw_signal)
            
            if red_dc > 0 and green_ac > 0 and green_dc > 0:
                ratio = (red_ac / red_dc) / (green_ac / green_dc)
                spo2 = 110 - (25 * ratio)
                spo2 = max(80.0, min(100.0, spo2)) # Clamp

        # Average Asymmetry
        avg_asym = float(np.mean(asymmetry_scores)) if asymmetry_scores else 0.0
        
        # Determine Risk Level
        risk_level = "GREEN"
        if bpm and (bpm > 100 or bpm < 50): risk_level = "YELLOW"
        if spo2 < 94: risk_level = "YELLOW"
        if avg_asym > 0.15: risk_level = "YELLOW" # Potential facial droop
        
        if (bpm and (bpm > 130 or bpm < 40)) or spo2 < 90 or avg_asym > 0.25:
            risk_level = "RED"

        return {
            "heart_rate": float(bpm) if bpm else None,
            "spo2_estimate": float(spo2),
            "asymmetry_score": float(avg_asym),
            "snr": float(snr),
            "risk_level": risk_level,
            "face_detected_ratio": float(face_detected_count / frame_count) if frame_count > 0 else 0,
            "frames_processed": frame_count,
            "fps": fps
        }
