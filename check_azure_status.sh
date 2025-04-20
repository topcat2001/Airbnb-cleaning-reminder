#!/bin/bash

# Script to check the status of the Airbnb Cleaning Reminder service on Azure

# Variables
REMOTE_USER="topcat"
REMOTE_HOST="20.163.12.101"

# Check if the server is reachable
echo "Checking if the server is reachable..."
ping -c 1 ${REMOTE_HOST} > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Cannot reach the server at ${REMOTE_HOST}"
    exit 1
fi

# Check the status of the service and timer
echo "Checking the status of the Airbnb Cleaning Reminder service and timer..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    echo "\n--- Service Status ---"
    sudo systemctl status airbnb-cleaner.service
    
    echo "\n--- Timer Status ---"
    sudo systemctl status airbnb-cleaner.timer
    
    echo "\n--- Timer List ---"
    sudo systemctl list-timers | grep airbnb
    
    echo "\n--- Last 20 Log Entries ---"
    tail -n 20 ~/airbnb-cleaning-reminder/cleaning_log.txt
    
    echo "\n--- Installed Python Packages ---"
    ~/airbnb-cleaning-reminder/venv/bin/pip list | grep -E "twilio|requests|icalendar"
    
    echo "\n--- Current Config ---"
    cat ~/airbnb-cleaning-reminder/config.json | grep -v "API_TOKEN\|SECRET"
EOF
