import mediapipe as mp
try:
    print(f"MediaPipe Version: {mp.__version__}")
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
    print("MediaPipe FaceMesh initialized successfully.")
    face_mesh.close()
except Exception as e:
    print(f"Error initializing MediaPipe: {e}")
    import traceback
    traceback.print_exc()
