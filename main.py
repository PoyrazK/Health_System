import cv2
import time
import numpy as np

from sensors.camera import CameraStream
from sensors.quality import SignalQuality
from processors.face_mesh import FaceMeshWrapper
from processors.rppg import RPPGProcessor
from processors.geometry import FaceGeometry
from ui.visualizer import Visualizer
from core.triage import TriageEngine

def main():
    print("[System] Medical Health Monitor Starting...")
    print("[System] Initializing Sensors & Models...")
    
    # 1. Initialize Components
    cam = CameraStream(src=0).start()
    face_mesh = FaceMeshWrapper(max_num_faces=1)
    rppg = RPPGProcessor(fps=30, buffer_size=300) 
    geometry = FaceGeometry()
    visualizer = Visualizer()
    triage = TriageEngine()
    triage.load_model() # Load the trained brain
    
    # Wait for camera to warm up
    time.sleep(1.0)
    print("[System] Ready. Press 'q' to quit.")
    
    # Moving Average Buffers
    bpm_history = []
    pupil_history = []
    pupil_history = []
    ear_history = []
    asym_history = []
    last_beep_time = 0
    
    try:
        while True:
            # 2. Capture
            frame, timestamp = cam.read()
            if frame is None:
                continue
                
            # Mirror for better UX
            frame = cv2.flip(frame, 1)
            
            metrics = {}
            status_msg = "Initializing..."
            
            # 3. Signal Quality Check
            is_bright_enough, light_msg, brightness = SignalQuality.check_brightness(frame)
            if not is_bright_enough:
                status_msg = light_msg
                metrics["Status"] = "BAD_LIGHT"
            else:
                # 4. Face Processing
                results = face_mesh.process(frame)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0]
                    
                    # 4.0 Head Pose Check (Are you looking at me?)
                    is_facing_camera, pose_msg = geometry.check_head_pose(landmarks)
                    if not is_facing_camera:
                        metrics["ALERT"] = pose_msg
                        
                        # Visual Warning
                        # Ensure this is drawn ON TOP of the visualizer if possible, 
                        # but visualizer draw comes later. So we should move this drawing AFTER visualizer.
                        # For now, let's keep it here but make sure it's big.
                        cv2.putText(frame, "LOOK AT CAMERA", (280, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
                        
                        # Audio Warning (Beep every 1.5s)
                        current_time = time.time()
                        if current_time - last_beep_time > 1.5:
                            import winsound
                            # Frequency 1000Hz, Duration 200ms, Async (SND_ASYNC is for PlaySound, Beep is blocking?)
                            # usage: winsound.Beep(frequency, duration)
                            # Beep is blocking. Use PlaySound for async or just accept tiny freeze? 
                            # 100ms freeze is okay.
                            try:
                                winsound.Beep(1000, 100)
                            except: pass
                            last_beep_time = current_time
                    
                    # Stabilize & Detailed Analysis
                    
                    # 1. EAR (Eye Aspect Ratio)
                    ear_left = geometry.calculate_ear(landmarks, geometry.LEFT_EYE)
                    ear_right = geometry.calculate_ear(landmarks, geometry.RIGHT_EYE)
                    avg_ear = (ear_left + ear_right) / 2.0
                    
                    ear_history.append(avg_ear)
                    if len(ear_history) > 10: ear_history.pop(0)
                    stable_ear = sum(ear_history) / len(ear_history)
                    
                    metrics["EAR"] = f"{stable_ear:.2f}"
                    metrics["EAR (L/R)"] = f"{ear_left:.2f} / {ear_right:.2f}" # Detail
                    
                    # 2. Asymmetry (Mouth)
                    asymmetry_score, symmetry_status = geometry.check_asymmetry(landmarks)
                    
                    asym_history.append(asymmetry_score)
                    if len(asym_history) > 15: asym_history.pop(0)
                    stable_asym = sum(asym_history) / len(asym_history)
                    
                    metrics["Asymmetry"] = f"{stable_asym:.2f}"
                    metrics["Status"] = symmetry_status # Warning/Normal
                    
                    # 4.1b Pupil Size (Iris Diameter)
                    # Note: This is in pixels and depends on distance
                    h, w, _ = frame.shape
                    iris_px = geometry.calculate_iris_diameter(landmarks, w, h)
                    
                    # Stabilize Pupil
                    pupil_history.append(iris_px)
                    if len(pupil_history) > 20: pupil_history.pop(0) # Smooth over 20 frames
                    avg_pupil = sum(pupil_history) / len(pupil_history)
                    
                    metrics["Pupil Size"] = f"{avg_pupil:.1f} px"

                    
                    # 4.2 Signal Extraction (rPPG)
                    mean_color, roi_points = face_mesh.get_roi_average(frame, landmarks, face_mesh.ROIS['right_cheek'])
                    
                    current_bpm = 0
                    if mean_color is not None:
                        green_val = mean_color[1]
                        rppg.add_sample(green_val, timestamp)
                        bpm = rppg.process()
                        
                        if bpm:
                            # Stabilize with Smart Smoothing
                            # 1. Outlier Check
                            if len(bpm_history) > 0:
                                last_avg = sum(bpm_history) / len(bpm_history)
                                diff = abs(bpm - last_avg)
                                
                                # If sudden jump > 30 BPM, ignore it (unless we have very few samples)
                                if diff > 30 and len(bpm_history) > 10:
                                    metrics["Status"] = "STABILIZING..."
                                    continue 
                            
                            # 2. Moving Average (Increased Buffer)
                            bpm_history.append(bpm)
                            if len(bpm_history) > 30: bpm_history.pop(0) # 30 samples ~ 1 sec
                            
                            avg_bpm = sum(bpm_history) / len(bpm_history)
                            
                            current_bpm = int(avg_bpm)
                            metrics["Heart Rate"] = f"{current_bpm} BPM"
                            metrics["Status"] = "MEASURING"
                        else:
                            metrics["Heart Rate"] = "Calibrating..."
                    
                    # 4.3 TRIAGE Intelligence (The Brain)
                    width = frame.shape[1]
                    # 4.3 TRIAGE Intelligence (The Brain)
                    if current_bpm > 0 and is_facing_camera:
                        risk_label, emergency_rate = triage.predict_detailed(
                            hr=current_bpm, 
                            spo2=98, 
                            asymmetry=asymmetry_score, 
                            ear=avg_ear
                        )
                        percentage = int(emergency_rate * 100)
                        metrics["Risk"] = f"{risk_label}"
                        metrics["Emergency Rate"] = f"{percentage}%"
                        
                        # Dynamic Color for Rate (Neon Palette BGR)
                        color = (50, 255, 50) # Neon Green
                        if percentage > 40: color = (0, 255, 255) # Neon Yellow
                        if percentage > 70: color = (50, 50, 255) # Neon Red
                        
                        # Bar Visualization (Top of screen)
                        bar_width = int((percentage / 100.0) * width)
                        cv2.rectangle(frame, (0,0), (bar_width, 20), color, -1)
                        if percentage > 0:
                             cv2.putText(frame, f"EMERGENCY RATE: {percentage}%", (width//2 - 100, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                        if "RED" in risk_label:
                            cv2.rectangle(frame, (0,0), (frame.shape[1], frame.shape[0]), (0,0,255), 5)
                            
                    # Graph Update
                    # Ideally use the filtered signal from rppg
                    if hasattr(rppg, 'latest_filtered_samples') and len(rppg.latest_filtered_samples) > 0:
                        val = rppg.latest_filtered_samples[-1]
                        # Normalize roughly for graph (-2 to +2 range usually)
                        visualizer.update_graph(val)
                    elif mean_color is not None:
                         # Fallback to raw
                         visualizer.update_graph( (mean_color[1] - 100) / 100.0 )
                    
                else:
                    status_msg = "No Face Detected"
                    metrics["Status"] = "SEARCHING"

            # 5. UI Rendering
            if "Status" not in metrics:
                 metrics["Status"] = status_msg
            
            frame = visualizer.draw(frame, metrics)
            
            # 6. Data Logging (For future ML Training)
            # Format: Timestamp, HeartRate, EAR, Asymmetry, Status
            if "Heart Rate" in metrics and "BPM" in metrics["Heart Rate"]:
                hr_val = metrics["Heart Rate"].replace(" BPM", "")
                ear_val = metrics.get("EAR", "0")
                asym_val = metrics.get("Asymmetry", "0").split(" ")[0]
                
                with open("health_data.csv", "a") as f:
                    f.write(f"{timestamp},{hr_val},{ear_val},{asym_val}\n")

            cv2.imshow('Mediapipe Health Monitor', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("[System] Interrupted.")
    finally:
        cam.stop()
        cv2.destroyAllWindows()
        print("[System] Shutdown complete.")

if __name__ == "__main__":
    main()
