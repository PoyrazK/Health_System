import cv2
import numpy as np
import os
import random

def create_synthetic_dataset(root_path, num_subjects=3):
    """
    Creates a fake UBFC-style dataset for testing the pipeline.
    Generates:
    - vid.avi: A 10-second video of a red circle pulsing (simulating heart beat)
    - ground_truth.txt: A file containing the fake HR (e.g. 75 BPM)
    """
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    
    print(f"[Synthetic] Generating {num_subjects} fake subjects in {root_path}...")
    
    for i in range(num_subjects):
        subj_dir = os.path.join(root_path, f"subject_{i+1}")
        if not os.path.exists(subj_dir):
            os.makedirs(subj_dir)
            
        # 1. Generate Fake Heart Rate
        target_bpm = random.randint(60, 100)
        
        # 2. Generate Video
        width, height = 640, 480
        fps = 30
        duration_sec = 10
        out_vid = os.path.join(subj_dir, "vid.avi")
        
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(out_vid, fourcc, fps, (width, height))
        
        for frame_idx in range(fps * duration_sec):
            # Pulsing Red Channel
            # frequency = BPM / 60
            freq = target_bpm / 60.0
            t = frame_idx / fps
            intensity = 127 + 50 * np.sin(2 * np.pi * freq * t)
            
            # Create a frame with a face-like color but pulsing
            # BGR format
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:] = (100, int(intensity), 100) # Green channel pulse
            
            # Draw a face circle
            cv2.circle(frame, (320, 240), 100, (150, int(intensity) + 20, 150), -1)
            
            out.write(frame)
            
        out.release()
        
        # 3. Generate Ground Truth
        # UBFC format usually has arrays, but our loader supports simple reading.
        # We will write a format that our loader expects (or update loader to match this)
        # Let's write just the HR for simplicity, or mimic the 3-row format
        gt_path = os.path.join(subj_dir, "ground_truth.txt")
        
        # Simulating 3 rows: Signal, HR, SpO2
        # We just put target_bpm in row 2
        with open(gt_path, 'w') as f:
            # Row 1: Fake Signal
            f.write("0 0 0\n") 
            # Row 2: HR (Constant)
            f.write(f"{target_bpm} {target_bpm} {target_bpm}\n")
            # Row 3: SpO2
            f.write("98 98 98\n")
            
        print(f"  -> Created Subject {i+1} (Target: {target_bpm} BPM)")

if __name__ == "__main__":
    create_synthetic_dataset("C:/Datasets/UBFC_rPPG")
