#!/bin/bash

# Deployment script for Twilio files

# Variables
REMOTE_USER="topcat"
REMOTE_HOST="20.163.12.101"
REMOTE_DIR="/home/topcat/airbnb-cleaning-reminder"
LOCAL_DIR="$(pwd)"

# Skip ping check as it might be blocked
echo "Attempting to connect to the server via SSH..."

# Copy the Twilio files to the remote server
echo "Copying Twilio files to the remote server..."
scp "${LOCAL_DIR}/airbnb_cleaner_notification.py" \
    "${LOCAL_DIR}/requirements.txt" \
    "${LOCAL_DIR}/test_twilio.py" \
    "${LOCAL_DIR}/check_message_status.py" \
    "${LOCAL_DIR}/config.json" \
    ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

# Set up Twilio on the remote server
echo "Setting up Twilio on the remote server..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    cd ~/airbnb-cleaning-reminder
    
    # Install Twilio
    echo "Installing Twilio..."
    ./venv/bin/pip install twilio
    
    # Restart the service and timer
    echo "Restarting the service and timer..."
    sudo systemctl stop airbnb-cleaner.service || true
    sudo systemctl stop airbnb-cleaner.timer || true
    sudo systemctl daemon-reload
    sudo systemctl enable airbnb-cleaner.timer
    sudo systemctl start airbnb-cleaner.timer
    
    # Test the Twilio integration
    echo "Testing the Twilio integration..."
    ./venv/bin/python test_twilio.py
    
    echo "Deployment completed successfully!"
    echo "The script will run automatically every day at 4 PM PST (midnight UTC)."
    echo "To check the timer status, run: systemctl status airbnb-cleaner.timer"
    echo "To check the service status, run: systemctl status airbnb-cleaner.service"
    echo "To view logs, check: ~/airbnb-cleaning-reminder/cleaning_log.txt"
EOF
