"""GIVE THE DATA OF ATTENTION DETECTOR WITHOUT FACE MESH AND ANY FRONTEND JUST A SIMPLE CODE WITH LIVE CAMERA FEED"""

import cv2
import mediapipe as mp
import numpy as np
import os
import time

# Disable MediaPipe logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Disable GPU to avoid some errors

# Initialize MediaPipe solutions with less verbose logging
mp_face_mesh = mp.solutions.face_mesh

# Initialize face mesh detector with more forgiving parameters
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.3,  # Lower threshold for easier detection
    min_tracking_confidence=0.3    # Lower threshold for easier tracking
)

# Eye landmarks
LEFT_EYE = [33, 159, 158, 133, 153, 144]
RIGHT_EYE = [362, 386, 385, 263, 373, 380]

# Define error margin
ERROR_MARGIN = 0.05

def get_face_orientation(landmarks, error_margin=0.05):
    """
    Check if face is oriented forward
    """
    try:
        # Get coordinates of key face landmarks
        nose = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])
        chin = np.array([landmarks[199].x, landmarks[199].y, landmarks[199].z])
        forehead = np.array([landmarks[10].x, landmarks[10].y, landmarks[10].z])
        
        # Calculate face orientation vector
        face_vector = forehead - chin
        
        # Add error margin to thresholds
        orientation_threshold = 0.15 + error_margin
        depth_threshold = 0.05 + error_margin
        
        return abs(face_vector[0]) < orientation_threshold and abs(face_vector[2]) < depth_threshold
    except (IndexError, AttributeError):
        return False

def get_face_position(landmarks, error_margin=0.05):
    """
    Check if the face is centered in the frame
    """
    try:
        # Use nose tip as reference point
        nose_x = landmarks[1].x
        
        # Check if nose is centered with error margin
        lower_bound = 0.35 - error_margin
        upper_bound = 0.65 + error_margin
        
        return lower_bound < nose_x < upper_bound
    except (IndexError, AttributeError):
        return False

def get_ear(landmarks, idxs):
    """Calculate the eye aspect ratio"""
    try:
        def p(i): return np.array([landmarks[idxs[i]].x, landmarks[idxs[i]].y])
        v = np.linalg.norm(p(1)-p(4)) + np.linalg.norm(p(2)-p(3))
        h = 2.0 * np.linalg.norm(p(0)-p(5))
        return v / h if h > 0 else 0
    except (IndexError, AttributeError):
        return 0

def main():
    print("Starting attention detector...")
    print("Press ESC to exit")
    
    # Try multiple camera indices if one fails
    camera_index = 0
    cap = None
    
    # Try camera indices 0-3
    for i in range(4):
        print(f"Trying camera at index {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_index = i
            print(f"Successfully opened camera at index {i}")
            break
    
    # If no camera could be opened
    if cap is None or not cap.isOpened():
        print("Error: Could not open any camera. Please check your camera connection.")
        return
    
    # Give camera time to warm up
    print("Warming up camera...")
    time.sleep(2)
    
    # Read test frame
    ret, test_frame = cap.read()
    if not ret or test_frame is None:
        print("Error: Camera is not providing frames. Please check your camera.")
        cap.release()
        return
    
    print(f"Camera resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
    print("Starting main loop...")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to grab frame, retrying...")
                time.sleep(0.5)
                continue
            
            frame_count += 1
            if frame_count % 30 == 0:  # Log FPS every 30 frames
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"FPS: {fps:.1f}")
            
            # Convert to RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = face_mesh.process(rgb)
    
            # Initialize status variables
            face_centered = False
            face_forward = False
            eyes_open = False
    
            # Process face mesh results
            if results.multi_face_landmarks:
                # Get first face landmarks
                landmarks = results.multi_face_landmarks[0].landmark
                
                # Check face position
                face_centered = get_face_position(landmarks, ERROR_MARGIN)
                
                # Check face orientation
                face_forward = get_face_orientation(landmarks, ERROR_MARGIN)
                
                # Check if eyes are open
                eye_threshold = 0.20 - ERROR_MARGIN
                left_ear = get_ear(landmarks, LEFT_EYE)
                right_ear = get_ear(landmarks, RIGHT_EYE)
                eyes_open = ((left_ear + right_ear) / 2) > eye_threshold
    
            # Determine overall status
            status = "Attentive" if face_centered and face_forward and eyes_open else "Not Attentive"
            color = (0, 255, 0) if status == "Attentive" else (0, 0, 255)
    
            # Display status
            cv2.putText(frame, f"Status: {status}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            # Show the frame
            cv2.imshow("Attention Detector", frame)
            
            # Exit on ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("ESC pressed, exiting...")
                break
    
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