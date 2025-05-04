// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const trackingTime = document.getElementById('trackingTime');
const attentivenessBar = document.getElementById('attentivenessBar');
const attentivenessText = document.getElementById('attentivenessText');
const progressCircle = document.getElementById('progressCircle');
const currentStatus = document.getElementById('currentStatus');
const trackingStatus = document.getElementById('trackingStatus');
const videoContainer = document.querySelector('.video-container');
const attentiveTime = document.getElementById('attentiveTime');
const distractedTime = document.getElementById('distractedTime');
const focusCycles = document.getElementById('focusCycles');

// State variables
let isTracking = false;
let statsInterval = null;
let totalAttentiveTime = 0;
let totalDistractionTime = 0;
let cycleCount = 0;
let lastStatus = '';

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('Attention Tracker application loaded');
    
    startBtn.addEventListener('click', startTracking);
    stopBtn.addEventListener('click', stopTracking);
    
    // Initialize summary values
    attentiveTime.textContent = formatTime(0);
    distractedTime.textContent = formatTime(0);
    focusCycles.textContent = '0';
    
    // Add smooth animations
    addAnimations();
});

// Format time as HH:MM:SS
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${hours}:${minutes}:${secs}`;
}

// Add animations to elements
function addAnimations() {
    document.querySelectorAll('.stat-card').forEach((card, index) => {
        card.style.animationDelay = `${0.1 * (index + 1)}s`;
    });
}

// Start tracking function
function startTracking() {
    console.log('Starting tracking...');
    
    // Call the backend to start tracking
    fetch('/start_tracking')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                isTracking = true;
                updateButtonStates();
                
                // Update UI to tracking state
                videoContainer.classList.add('tracking');
                trackingStatus.innerHTML = '<span class="dot"></span> Tracking';
                
                // Reset summary data if needed
                if (!statsInterval) {
                    totalAttentiveTime = 0;
                    totalDistractionTime = 0;
                    cycleCount = 0;
                    attentiveTime.textContent = formatTime(0);
                    distractedTime.textContent = formatTime(0);
                    focusCycles.textContent = '0';
                }
                
                // Start updating stats
                startStatsUpdates();
                
                console.log('Tracking started successfully');
            }
        })
        .catch(error => {
            console.error('Error starting tracking:', error);
        });
}

// Stop tracking function
function stopTracking() {
    console.log('Stopping tracking...');
    
    // Call the backend to stop tracking
    fetch('/stop_tracking')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'stopped') {
                isTracking = false;
                updateButtonStates();
                
                // Update UI to non-tracking state
                videoContainer.classList.remove('tracking');
                trackingStatus.innerHTML = '<span class="dot"></span> Not Tracking';
                
                // Stop updating stats
                stopStatsUpdates();
                
                console.log('Tracking stopped successfully');
            }
        })
        .catch(error => {
            console.error('Error stopping tracking:', error);
        });
}

// Start stats update timer
function startStatsUpdates() {
    // Clear any existing interval
    if (statsInterval) {
        clearInterval(statsInterval);
    }
    
    // Update stats immediately
    updateStats();
    
    // Then set interval to update every second
    statsInterval = setInterval(updateStats, 1000);
}

// Stop stats update timer
function stopStatsUpdates() {
    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }
}

// Update stats from backend
function updateStats() {
    fetch('/get_stats')
        .then(response => response.json())
        .then(data => {
            // Update tracking time
            trackingTime.textContent = data.elapsed_time;
            
            // Update attentiveness percentage
            const attentiveness = data.attentiveness;
            attentivenessBar.style.width = `${attentiveness}%`;
            attentivenessBar.textContent = `${attentiveness}%`;
            
            // Update progress circle
            progressCircle.style.setProperty('--progress', `${attentiveness}%`);
            attentivenessText.textContent = `${attentiveness}%`;
            
            // Update color based on attentiveness
            if (attentiveness >= 70) {
                attentivenessBar.style.background = 'linear-gradient(90deg, #2ecc71, #27ae60)';
            } else if (attentiveness >= 40) {
                attentivenessBar.style.background = 'linear-gradient(90deg, #f39c12, #e67e22)';
            } else {
                attentivenessBar.style.background = 'linear-gradient(90deg, #e74c3c, #c0392b)';
            }
            
            // Update current status and calculate summary stats
            if (!data.is_tracking) {
                currentStatus.textContent = 'Not Tracking';
                currentStatus.className = 'stat-value status-not-tracking';
                videoContainer.classList.remove('tracking');
                trackingStatus.innerHTML = '<span class="dot"></span> Not Tracking';
            } else {
                currentStatus.textContent = data.current_status;
                
                // Track focus cycles
                if (lastStatus !== data.current_status) {
                    if (data.current_status === 'Attentive' && lastStatus === 'Not Attentive') {
                        cycleCount++;
                        focusCycles.textContent = cycleCount;
                    }
                    lastStatus = data.current_status;
                }
                
                // Update time counters
                if (data.current_status === 'Attentive') {
                    currentStatus.className = 'stat-value status-attentive';
                    totalAttentiveTime++;
                    attentiveTime.textContent = formatTime(totalAttentiveTime);
                } else {
                    currentStatus.className = 'stat-value status-not-attentive';
                    totalDistractionTime++;
                    distractedTime.textContent = formatTime(totalDistractionTime);
                }
            }
            
            // Ensure button states match the backend state
            isTracking = data.is_tracking;
            updateButtonStates();
            
            // Update tracking status in UI
            if (isTracking) {
                videoContainer.classList.add('tracking');
                trackingStatus.innerHTML = '<span class="dot"></span> Tracking';
            } else {
                videoContainer.classList.remove('tracking');
                trackingStatus.innerHTML = '<span class="dot"></span> Not Tracking';
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Update button states based on tracking status
function updateButtonStates() {
    if (isTracking) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// Adjust video container height based on window size if needed
function adjustVideoHeight() {
    const windowHeight = window.innerHeight;
    const videoContainer = document.querySelector('.video-container');
    
    if (windowHeight < 800) {
        videoContainer.style.height = '350px';
    } else if (windowHeight < 1000) {
        videoContainer.style.height = '400px';
    } else {
        videoContainer.style.height = '500px';
    }
}

// Adjust video height on load and resize
window.addEventListener('load', adjustVideoHeight);
window.addEventListener('resize', adjustVideoHeight);