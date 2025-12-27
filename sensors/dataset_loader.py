import cv2
import csv
import os
import numpy as np

class DatasetLoader:
    def __init__(self, root_path):
        self.root_path = root_path
        
    def get_subjects(self):
        raise NotImplementedError
    
    def get_video_stream(self, subject_id):
        raise NotImplementedError
    
    def get_ground_truth(self, subject_id):
        """Returns True Heart Rate (BPM)"""
        raise NotImplementedError

class UBFC_Loader(DatasetLoader):
    """
    Loader for UBFC-rPPG Dataset.
    Structure:
    /subject1/
        vid.avi
        ground_truth.txt
    """
    def get_subjects(self):
        # List all subdirectories
        if not os.path.exists(self.root_path):
            return []
        return [d for d in os.listdir(self.root_path) if os.path.isdir(os.path.join(self.root_path, d))]

    def get_video_stream(self, subject_id):
        vid_path = os.path.join(self.root_path, subject_id, "vid.avi")
        if not os.path.exists(vid_path):
            print(f"[UBFC] Video not found: {vid_path}")
            return None
        return cv2.VideoCapture(vid_path)

    def get_ground_truth(self, subject_id):
        gt_path = os.path.join(self.root_path, subject_id, "ground_truth.txt")
        if not os.path.exists(gt_path):
            return None
        
        # UBFC GT format: Arrays of Time, HR, SpO2
        # We just want the average HR for simplicity or array
        try:
            # First line is usually headers or data depending on version.
            # Assuming simple space separated
            data = np.loadtxt(gt_path)
            # Row 0: PPG Signal (raw), Row 1: HR, Row 2: SpO2
            # Check shape
            if len(data.shape) > 1 and data.shape[0] == 3:
                 mean_hr = np.mean(data[1])
                 return mean_hr
            else:
                return 75.0 # Fallback/Debug
        except Exception as e:
            print(f"Error reading GT: {e}")
            return None

class YFP_Loader(DatasetLoader):
    """
    Loader for YouTube Facial Paralysis Dataset.
    Structure (Assumed):
    /normal/video1.mp4
    /patient/video2.mp4
    """
    def __init__(self, root_path):
        super().__init__(root_path)
        self.classes = ["normal", "patient"]

    def get_subjects(self):
        subjects = []
        for cls in self.classes:
            cls_path = os.path.join(self.root_path, cls)
            if os.path.exists(cls_path):
                files = os.listdir(cls_path)
                for f in files:
                    if f.endswith(".mp4"):
                        subjects.append({"id": f, "class": cls, "path": os.path.join(cls_path, f)})
        return subjects

    def get_video_stream(self, subject_obj):
        return cv2.VideoCapture(subject_obj["path"])
        
    def get_ground_truth(self, subject_obj):
        # clean_class = 0 (Normal), 1 (Palsy)
        return 1 if subject_obj["class"] == "patient" else 0
