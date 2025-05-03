"""THE MAIN BACKEND FOR THE ATTENTION DETECTOR AND THE MOST IMPORTANT PART OF THE CODE"""
from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import os
import time
import threading

app = Flask(__name__, static_folder='static')

# Global variables
global_frame = None
global_status = "Not started"
start_time = None
total_frames = 0
attentive_frames = 0
is_tracking = False

# Disable MediaPipe logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Disable GPU to avoid some errors

# Initialize MediaPipe solutions
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

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

def process_frames():
    global global_frame, global_status, start_time, total_frames, attentive_frames, is_tracking
    
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
        print("Error: Could not open any camera.")
        return
    
    # Give camera time to warm up
    print("Warming up camera...")
    time.sleep(2)
    
    frame_count = 0
    fps_start_time = time.time()
    fps = 0
    
    while True:
        # Break the loop if tracking is stopped
        if not is_tracking:
            time.sleep(0.1)  # Sleep to reduce CPU usage
            continue
            
        # Read frame
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to grab frame, retrying...")
            time.sleep(0.5)
            continue
        
        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:  # Update FPS every 30 frames
            current_time = time.time()
            elapsed = current_time - fps_start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            frame_count = 0
            fps_start_time = current_time
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
            
            # Face mesh drawing removed as requested
            # We still process the landmarks but don't draw them on the frame
            
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
        is_attentive = face_centered and face_forward and eyes_open
        status = "Attentive" if is_attentive else "Not Attentive"
        color = (0, 255, 0) if status == "Attentive" else (0, 0, 255)
        
        # Update metrics
        total_frames += 1
        if is_attentive:
            attentive_frames += 1
        
        # Create status overlay
        cv2.putText(frame, f"Status: {status}", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
        cv2.putText(frame, f"FPS: {fps:.1f}", (30, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Convert frame to JPEG for streaming
        _, buffer = cv2.imencode('.jpg', frame)
        global_frame = buffer.tobytes()
        global_status = status

def generate_frames():
    global global_frame
    while True:
        if global_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_tracking')
def start_tracking():
    global is_tracking, start_time, total_frames, attentive_frames
    is_tracking = True
    start_time = time.time()
    total_frames = 0
    attentive_frames = 0
    return jsonify({"status": "started"})

@app.route('/stop_tracking')
def stop_tracking():
    global is_tracking
    is_tracking = False
    return jsonify({"status": "stopped"})

@app.route('/get_stats')
def get_stats():
    global start_time, total_frames, attentive_frames, global_status, is_tracking
    
    if start_time is None:
        elapsed_time = 0
    else:
        elapsed_time = time.time() - start_time
    
    # Calculate attentiveness percentage
    if total_frames > 0:
        attentiveness = (attentive_frames / total_frames) * 100
    else:
        attentiveness = 0
    
    # Format time
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return jsonify({
        "elapsed_time": formatted_time,
        "attentiveness": round(attentiveness, 2),
        "current_status": global_status,
        "is_tracking": is_tracking
    })

if __name__ == "__main__":
    # Start the frame processing in a separate thread
    threading.Thread(target=process_frames, daemon=True).start()
    
    # Start the Flask app
    app.run(debug=True, threaded=True, use_reloader=False)