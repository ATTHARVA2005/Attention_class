import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

pose = mp_pose.Pose()
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

def get_posture_status(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    return shoulder_diff < 0.05  # smaller diff means straight

def get_eye_aspect_ratio(landmarks, indices):
    p1 = np.array([landmarks[indices[1]].x, landmarks[indices[1]].y])
    p2 = np.array([landmarks[indices[5]].x, landmarks[indices[5]].y])
    p3 = np.array([landmarks[indices[2]].x, landmarks[indices[2]].y])
    p4 = np.array([landmarks[indices[4]].x, landmarks[indices[4]].y])
    p5 = np.array([landmarks[indices[0]].x, landmarks[indices[0]].y])
    p6 = np.array([landmarks[indices[3]].x, landmarks[indices[3]].y])
    
    vertical = np.linalg.norm(p2 - p4) + np.linalg.norm(p3 - p5)
    horizontal = 2.0 * np.linalg.norm(p1 - p6)
    ear = vertical / horizontal
    return ear

# Eye landmarks (from MediaPipe Face Mesh)
LEFT_EYE = [33, 159, 158, 133, 153, 144]
RIGHT_EYE = [362, 386, 385, 263, 373, 380]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    pose_results = pose.process(rgb)
    face_results = face_mesh.process(rgb)

    posture_ok = False
    eyes_open = False

    if pose_results.pose_landmarks:
        posture_ok = get_posture_status(pose_results.pose_landmarks.landmark)

    if face_results.multi_face_landmarks:
        landmarks = face_results.multi_face_landmarks[0].landmark
        left_ear = get_eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = get_eye_aspect_ratio(landmarks, RIGHT_EYE)
        avg_ear = (left_ear + right_ear) / 2
        eyes_open = avg_ear > 0.20  # threshold based on typical EAR

    status = "Attentive" if posture_ok and eyes_open else "Not Attentive"
    color = (0, 255, 0) if status == "Attentive" else (0, 0, 255)

    cv2.putText(frame, f"Status: {status}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    
    cv2.imshow("Attention Detector", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
