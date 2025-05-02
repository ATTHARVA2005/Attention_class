from flask import Flask, render_template, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import base64

app = Flask(__name__)

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

pose = mp_pose.Pose()
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

LEFT_EYE = [33, 159, 158, 133, 153, 144]
RIGHT_EYE = [362, 386, 385, 263, 373, 380]

def get_posture_status(landmarks):
    left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    return abs(left.y - right.y) < 0.05

def get_ear(landmarks, idxs):
    def p(i): return np.array([landmarks[idxs[i]].x, landmarks[idxs[i]].y])
    v = np.linalg.norm(p(1)-p(4)) + np.linalg.norm(p(2)-p(3))
    h = 2.0 * np.linalg.norm(p(0)-p(5))
    return v / h

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])
    np_img = np.frombuffer(img_data, dtype=np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_result = pose.process(rgb)
    face_result = face_mesh.process(rgb)

    posture_ok = False
    eyes_open = False

    if pose_result.pose_landmarks:
        posture_ok = get_posture_status(pose_result.pose_landmarks.landmark)

    if face_result.multi_face_landmarks:
        lm = face_result.multi_face_landmarks[0].landmark
        left = get_ear(lm, LEFT_EYE)
        right = get_ear(lm, RIGHT_EYE)
        eyes_open = ((left + right) / 2) > 0.20

    status = "Attentive" if posture_ok and eyes_open else "Not Attentive"
    return jsonify({'status': status})

if __name__ == '__main__':
    app.run(debug=True)
