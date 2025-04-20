#!/bin/bash

# Deployment script for Airbnb Cleaning Reminder

# Variables
REMOTE_USER="topcat"
REMOTE_HOST="20.163.12.101"
REMOTE_DIR="/home/topcat/airbnb-cleaning-reminder"
LOCAL_DIR="$(pwd)"

# Create the remote directory if it doesn't exist
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}"

# Copy the necessary files to the remote server
echo "Copying files to the remote server..."
scp "${LOCAL_DIR}/airbnb_cleaner_notification.py" \
    "${LOCAL_DIR}/requirements.txt" \
    "${LOCAL_DIR}/README.md" \
    "${LOCAL_DIR}/test_twilio.py" \
    "${LOCAL_DIR}/check_message_status.py" \
    "${LOCAL_DIR}/config.json" \
    ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

# Set up the Python environment on the remote server
echo "Setting up the Python environment on the remote server..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    cd ~/airbnb-cleaning-reminder
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Installing..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    else
        echo "Python 3 is already installed."
    fi
    
    # Install system packages
    echo "Installing system packages..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-full
    
    # Create and setup a virtual environment
    echo "Setting up a virtual environment..."
    python3 -m venv --system-site-packages venv
    
    # Install dependencies in the virtual environment
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    
    # Make the script executable
    chmod +x airbnb_cleaner_notification.py
    
    # Create a systemd service file
    echo "Creating a systemd service file..."
    sudo tee /etc/systemd/system/airbnb-cleaner.service > /dev/null << SERVICEEOF
[Unit]
Description=Airbnb Cleaning Reminder Service
After=network.target

[Service]
Type=oneshot
User=topcat
WorkingDirectory=/home/topcat/airbnb-cleaning-reminder
ExecStart=/home/topcat/airbnb-cleaning-reminder/venv/bin/python /home/topcat/airbnb-cleaning-reminder/airbnb_cleaner_notification.py
StandardOutput=append:/home/topcat/airbnb-cleaning-reminder/cleaning_log.txt
StandardError=append:/home/topcat/airbnb-cleaning-reminder/cleaning_log.txt

[Install]
WantedBy=multi-user.target
SERVICEEOF

    # Create a systemd timer file to run the service daily at 4 PM PST (UTC-8)
    # This is midnight UTC (00:00) during PST
    echo "Creating a systemd timer file to run at 4 PM PST daily..."
    sudo tee /etc/systemd/system/airbnb-cleaner.timer > /dev/null << TIMEREOF
[Unit]
Description=Run Airbnb Cleaning Reminder daily at 4 PM PST

[Timer]
OnCalendar=*-*-* 00:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
TIMEREOF

    # Stop any existing service and timer
    echo "Stopping any existing service and timer..."
    sudo systemctl stop airbnb-cleaner.service || true
    sudo systemctl stop airbnb-cleaner.timer || true

    # Enable and start the timer
    echo "Enabling and starting the timer..."
    sudo systemctl daemon-reload
    sudo systemctl enable airbnb-cleaner.timer
    sudo systemctl start airbnb-cleaner.timer
    
    echo "Deployment completed successfully!"
    echo "You can test the script by running: cd ~/airbnb-cleaning-reminder && ./venv/bin/python airbnb_cleaner_notification.py --dry-run"
    echo "The script will run automatically every day at 4 PM PST (midnight UTC)."
    echo "To check the timer status, run: systemctl status airbnb-cleaner.timer"
    echo "To check the service status, run: systemctl status airbnb-cleaner.service"
    echo "To view logs, check: ~/airbnb-cleaning-reminder/cleaning_log.txt"
EOF
