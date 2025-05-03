# AttentionMinder

![AttentionMinder Logo](https://img.shields.io/badge/Noobly%20Pros-AttentionMinder-4a6bff)

## 🏆 Project by Team "Noobly Pros"

AttentionMinder is an intelligent real-time attention monitoring system that helps users maintain focus during work or study sessions by tracking posture and eye status.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [How it Works](#how-it-works)
- [Future Enhancements](#future-enhancements)
- [Team Members](#team-members)
- [Acknowledgements](#acknowledgements)

## 📝 Overview

AttentionMinder uses computer vision to detect signs of inattention in real-time. By monitoring posture alignment and eye openness, the application provides immediate feedback to help users stay focused and maintain healthy work habits. Perfect for students, remote workers, and anyone who wants to improve their focus and productivity.

## ✨ Features

- **Real-time Posture Analysis**: Detects shoulder alignment to identify slouching or poor posture
- **Eye Status Monitoring**: Tracks whether eyes are open or closed to detect fatigue or distraction
- **Attention Timeline**: Visual history of attention status throughout each session
- **Attention Rate Calculation**: Overall percentage of time spent in an attentive state
- **Session Statistics**: Detailed breakdown of your focus metrics during each session
- **Privacy-Focused**: All processing happens locally in the browser - no video data is stored or transmitted

## 🔧 Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Flask (Python)
- **Computer Vision**: MediaPipe, OpenCV
- **Face & Pose Detection**: MediaPipe Face Mesh & Pose models

## 🔌 Installation

1. Clone the repository:
```bash
git clone https://github.com/ATTHARVA2005/Attention_class.git
cd Attention_class
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 🚀 Usage

1. When you first open the application, you'll be prompted to grant camera access
2. Click "Start Monitoring" to begin tracking your attention state
3. The dashboard will display your current posture and eye status in real-time
4. The timeline at the bottom shows your attention history throughout the session
5. When finished, click "Stop" to end the monitoring session and view your final stats

## 🧠 How it Works

AttentionMinder uses MediaPipe's pose estimation to detect shoulder alignment, which serves as an indicator of good posture. Simultaneously, it uses MediaPipe's face mesh detection to calculate the Eye Aspect Ratio (EAR), which helps determine if eyes are open or closed.

The application captures frames from your webcam at regular intervals and sends them to the Flask backend for analysis. The backend processes each frame using the following steps:

1. **Pose Detection**: Analyzes shoulder landmarks to ensure they're properly aligned
2. **Face Mesh Detection**: Locates facial landmarks, particularly around the eyes
3. **Eye Aspect Ratio Calculation**: Measures the openness of eyes using geometric relationships between eye landmarks
4. **Attention State Determination**: Combines posture and eye data to classify the current state as either "Attentive" or "Not Attentive"

## 🚀 Future Enhancements

- Audio alerts for prolonged periods of inattention
- Customizable sensitivity settings
- Attention history reports and analytics
- Integration with productivity apps
- Eye strain prevention features
- Machine learning to personalize detection based on individual posture differences

## 👥 Team Members

**Team Noobly Pros:**
- Attharva Gupta
- Anubhab Das

## 🙏 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) for their open-source computer vision models
- [Flask](https://flask.palletsprojects.com/) for the lightweight Python web framework
- [OpenCV](https://opencv.org/) for computer vision capabilities

---
