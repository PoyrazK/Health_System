import cv2
import time
import numpy as np
from sensors.dataset_loader import UBFC_Loader, YFP_Loader
from processors.face_mesh import FaceMeshWrapper
from processors.rppg import RPPGProcessor
from processors.geometry import FaceGeometry

def validation_loop(dataset_loader, task_type="rPPG"):
    print(f"[Validation] Starting loop for {task_type}...")
    
    subjects = dataset_loader.get_subjects()
    if not subjects:
        print("[Error] No subjects found in dataset path.")
        return

    face_mesh = FaceMeshWrapper(max_num_faces=1)
    geometry = FaceGeometry()
    
    results = []
    
    for subj in subjects:
        print(f"Processing {subj}...")
        cap = dataset_loader.get_video_stream(subj)
        if cap is None: continue
        
        gt_value = dataset_loader.get_ground_truth(subj)
        
        rppg = RPPGProcessor(fps=30)
        estimated_values = []
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Timestamp simulation (assuming 30fps)
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            
            results_mp = face_mesh.process(frame)
            if results_mp.multi_face_landmarks:
                landmarks = results_mp.multi_face_landmarks[0]
                
                if task_type == "rPPG":
                    mean_color, _ = face_mesh.get_roi_average(frame, landmarks, face_mesh.ROIS['right_cheek'])
                    if mean_color:
                        rppg.add_sample(mean_color[1], timestamp)
                        bpm = rppg.process()
                        if bpm: estimated_values.append(bpm)
                        
                elif task_type == "Palsy":
                    asym, _ = geometry.check_asymmetry(landmarks)
                    estimated_values.append(asym)
        
        cap.release()
        
        # Aggregate Result
        if estimated_values:
            final_est = np.mean(estimated_values)
            error = abs(final_est - gt_value)
            print(f"   -> True: {gt_value:.2f}, Est: {final_est:.2f}, Error: {error:.2f}")
            results.append({"Subject": subj, "True": gt_value, "Est": final_est, "Error": error})
        else:
            print("   -> No valid estimation.")

    # Final Report
    if results:
        df_errors = [r["Error"] for r in results]
        mae = np.mean(df_errors)
        print(f"\n[FINAL REPORT] {task_type}")
        print(f"Mean Absolute Error: {mae:.2f}")
    else:
        print("No results generated.")

if __name__ == "__main__":
    # Example Usage:
    # 1. Setup Loader
    loader = UBFC_Loader("C:/Datasets/UBFC_rPPG")
    validation_loop(loader, "rPPG")
    
    print("Validation Run Complete.")
