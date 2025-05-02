// script.js
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusText = document.getElementById('statusText');
    const statusIndicator = document.getElementById('statusIndicator');
    const postureStatus = document.getElementById('postureStatus');
    const eyeStatus = document.getElementById('eyeStatus');
    const monitoringTime = document.getElementById('monitoringTime');
    const attentionRate = document.getElementById('attentionRate');
    const timeline = document.getElementById('timeline');
    const permissionModal = document.getElementById('permissionModal');
    const grantPermissionBtn = document.getElementById('grantPermissionBtn');

    // App state
    let stream = null;
    let isMonitoring = false;
    let monitoringInterval = null;
    let startTime = null;
    let attentiveCount = 0;
    let totalSamples = 0;
    let timelineData = [];
    let analyzeCounter = 0;
    
    // Constants
    const ANALYZE_INTERVAL = 1000; // Time between analyses (ms)
    const TIMELINE_MAX_SEGMENTS = 60; // Maximum number of segments in timeline
    const CAMERA_CONSTRAINTS = {
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
        },
        audio: false
    };

    // Initialize timeline
    initializeTimeline();

    // Event listeners
    startBtn.addEventListener('click', startMonitoring);
    stopBtn.addEventListener('click', stopMonitoring);
    grantPermissionBtn.addEventListener('click', requestCameraPermission);

    // Show permission modal on first load
    showPermissionModal();

    // Functions
    function showPermissionModal() {
        permissionModal.classList.add('show');
    }

    function hidePermissionModal() {
        permissionModal.classList.remove('show');
    }

    async function requestCameraPermission() {
        try {
            stream = await navigator.mediaDevices.getUserMedia(CAMERA_CONSTRAINTS);
            video.srcObject = stream;
            hidePermissionModal();
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Could not access camera. Please allow camera access to use this application.');
        }
    }

    function startMonitoring() {
        if (!stream) {
            showPermissionModal();
            return;
        }

        isMonitoring = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        startTime = new Date();
        attentiveCount = 0;
        totalSamples = 0;
        
        // Reset timeline
        timelineData = Array(TIMELINE_MAX_SEGMENTS).fill(null);
        updateTimeline();

        // Start monitoring interval
        monitoringInterval = setInterval(monitorAttention, ANALYZE_INTERVAL);
        updateTimer();
        
        // Update UI
        statusText.textContent = "Starting monitoring...";
        statusIndicator.className = "status-indicator";
        statusIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span id="statusText">Starting monitoring...</span>';
    }

    function stopMonitoring() {
        isMonitoring = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        clearInterval(monitoringInterval);
        
        // Update UI
        statusText.textContent = "Monitoring stopped";
        statusIndicator.className = "status-indicator";
        statusIndicator.innerHTML = '<i class="fas fa-stop-circle"></i><span id="statusText">Monitoring stopped</span>';
    }

    function updateTimer() {
        if (!isMonitoring) return;
        
        const elapsedTime = new Date() - startTime;
        const hours = Math.floor(elapsedTime / 3600000).toString().padStart(2, '0');
        const minutes = Math.floor((elapsedTime % 3600000) / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((elapsedTime % 60000) / 1000).toString().padStart(2, '0');
        
        monitoringTime.textContent = `${hours}:${minutes}:${seconds}`;
        
        setTimeout(updateTimer, 1000);
    }

    function monitorAttention() {
        if (!isMonitoring) return;
        
        // Capture frame from video
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 for sending to server
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to server for analysis
        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            updateStatus(data.status);
        })
        .catch(error => {
            console.error('Error analyzing frame:', error);
            updateStatus('Error');
        });
    }

    function updateStatus(status) {
        // Update UI based on status
        totalSamples++;
        
        if (status === 'Attentive') {
            attentiveCount++;
            statusIndicator.className = "status-indicator attentive";
            statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i><span id="statusText">Attentive</span>';
            postureStatus.textContent = "Good posture";
            postureStatus.className = "good";
            eyeStatus.textContent = "Eyes open";
            eyeStatus.className = "good";
        } else {
            statusIndicator.className = "status-indicator not-attentive";
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span id="statusText">Not Attentive</span>';
            
            // Simulate more detailed status (in a real app, the server would provide this)
            if (Math.random() > 0.5) {
                postureStatus.textContent = "Poor posture";
                postureStatus.className = "bad";
                eyeStatus.textContent = "Eyes open";
                eyeStatus.className = "good";
            } else {
                postureStatus.textContent = "Good posture";
                postureStatus.className = "good";
                eyeStatus.textContent = "Eyes closed";
                eyeStatus.className = "bad";
            }
        }
        
        // Update attention rate
        const rate = Math.round((attentiveCount / totalSamples) * 100);
        attentionRate.textContent = `${rate}%`;
        
        // Update timeline
        analyzeCounter++;
        if (analyzeCounter % 5 === 0) { // Update timeline every 5 seconds
            timelineData.shift();
            timelineData.push(status === 'Attentive');
            updateTimeline();
        }
    }

    function initializeTimeline() {
        timelineData = Array(TIMELINE_MAX_SEGMENTS).fill(null);
        updateTimeline();
    }

    function updateTimeline() {
        // Clear timeline
        timeline.innerHTML = '';
        
        // Add segments
        timelineData.forEach(isAttentive => {
            const segment = document.createElement('div');
            segment.className = 'timeline-segment';
            
            if (isAttentive === null) {
                segment.classList.add('no-data');
            } else if (isAttentive) {
                segment.classList.add('attentive');
            } else {
                segment.classList.add('not-attentive');
            }
            
            timeline.appendChild(segment);
        });
    }
});