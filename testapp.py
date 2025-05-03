"""GIVES THE ATTENTION TRACKER DATA ALONG WITH FACE MESH AND LIVE CAMERA FEED FOR TESTING PURPOSES"""
import cv2
import mediapipe as mp
import numpy as np
import os
import time
from datetime import timedelta

# Disable MediaPipe logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Initialize face mesh detector
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)

# Eye landmarks
LEFT_EYE = [33, 159, 158, 133, 153, 144]
RIGHT_EYE = [362, 386, 385, 263, 373, 380]

ERROR_MARGIN = 0.05

def get_face_orientation(landmarks, error_margin=0.05):
    try:
        nose = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])
        chin = np.array([landmarks[199].x, landmarks[199].y, landmarks[199].z])
        forehead = np.array([landmarks[10].x, landmarks[10].y, landmarks[10].z])
        face_vector = forehead - chin
        orientation_threshold = 0.15 + error_margin
        depth_threshold = 0.05 + error_margin
        return abs(face_vector[0]) < orientation_threshold and abs(face_vector[2]) < depth_threshold
    except (IndexError, AttributeError):
        return False

def get_face_position(landmarks, error_margin=0.05):
    try:
        nose_x = landmarks[1].x
        lower_bound = 0.35 - error_margin
        upper_bound = 0.65 + error_margin
        return lower_bound < nose_x < upper_bound
    except (IndexError, AttributeError):
        return False

def get_ear(landmarks, idxs):
    try:
        def p(i): return np.array([landmarks[idxs[i]].x, landmarks[idxs[i]].y])
        v = np.linalg.norm(p(1)-p(4)) + np.linalg.norm(p(2)-p(3))
        h = 2.0 * np.linalg.norm(p(0)-p(5))
        return v / h if h > 0 else 0
    except (IndexError, AttributeError):
        return 0

def main():
    print("Starting Attention Tracker...")
    print("Press ESC to exit, 'r' to reset statistics")

    cap = None
    for i in range(4):
        print(f"Trying camera at index {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera opened at index {i}")
            break

    if cap is None or not cap.isOpened():
        print("Error: Could not open any camera.")
        return

    print("Warming up camera...")
    time.sleep(2)

    ret, test_frame = cap.read()
    if not ret or test_frame is None:
        print("Error: Camera is not providing frames.")
        cap.release()
        return

    height, width = test_frame.shape[:2]
    print(f"Camera resolution: {width}x{height}")

    start_time = time.time()
    total_frames = 0
    attentive_frames = 0
    fps_start_time = time.time()
    frame_count = 0
    fps = 0

    window_name = "Attention Tracker"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    # Custom green mesh style
    GREEN_MESH = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to grab frame, retrying...")
                time.sleep(0.5)
                continue

            frame_count += 1
            current_time = time.time()
            if current_time - fps_start_time >= 1:
                fps = frame_count / (current_time - fps_start_time)
                frame_count = 0
                fps_start_time = current_time

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            face_centered = False
            face_forward = False
            eyes_open = False

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                face_centered = get_face_position(landmarks, ERROR_MARGIN)
                face_forward = get_face_orientation(landmarks, ERROR_MARGIN)

                eye_threshold = 0.20 - ERROR_MARGIN
                left_ear = get_ear(landmarks, LEFT_EYE)
                right_ear = get_ear(landmarks, RIGHT_EYE)
                eyes_open = ((left_ear + right_ear) / 2) > eye_threshold

                # ✅ Draw only green tessellation, no eyes/lips/contours
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=GREEN_MESH
                    )

            is_attentive = face_centered and face_forward and eyes_open
            status = "Attentive" if is_attentive else "Not Attentive"
            color = (0, 255, 0) if is_attentive else (0, 0, 255)

            total_frames += 1
            if is_attentive:
                attentive_frames += 1

            elapsed_time = time.time() - start_time
            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            attentiveness = (attentive_frames / total_frames * 100) if total_frames > 0 else 0

            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (width - 20, 160), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            cv2.putText(frame, f"Status: {status}", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Time: {elapsed_str}", (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Attentiveness: {attentiveness:.1f}%", (30, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"FPS: {fps:.1f}", (width - 120, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("ESC pressed, exiting...")
                break
            elif key == ord('r'):
                print("Resetting statistics...")
                start_time = time.time()
                total_frames = 0
                attentive_frames = 0

    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        print("Cleaning up resources...")
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        print("Done.")

if __name__ == "__main__":
    main()
