// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const trackingTime = document.getElementById('trackingTime');
const attentivenessBar = document.getElementById('attentivenessBar');
const currentStatus = document.getElementById('currentStatus');

// State variables
let isTracking = false;
let statsInterval = null;

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('Attention Tracker application loaded');
    
    startBtn.addEventListener('click', startTracking);
    stopBtn.addEventListener('click', stopTracking);
});

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
            
            // Update color based on attentiveness
            if (attentiveness >= 70) {
                attentivenessBar.style.backgroundColor = '#38a169'; // Green
            } else if (attentiveness >= 40) {
                attentivenessBar.style.backgroundColor = '#ecc94b'; // Yellow
            } else {
                attentivenessBar.style.backgroundColor = '#e53e3e'; // Red
            }
            
            // Update current status
            if (!data.is_tracking) {
                currentStatus.textContent = 'Not Tracking';
                currentStatus.className = 'stat-value status-not-tracking';
            } else {
                currentStatus.textContent = data.current_status;
                
                if (data.current_status === 'Attentive') {
                    currentStatus.className = 'stat-value status-attentive';
                } else {
                    currentStatus.className = 'stat-value status-not-attentive';
                }
            }
            
            // Ensure button states match the backend state
            isTracking = data.is_tracking;
            updateButtonStates();
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