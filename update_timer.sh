#!/bin/bash

# Script to update the timer for Airbnb Cleaning Reminder to run at 4:45 PM Pacific time

echo "Updating the timer to run at 4:45 PM Pacific time..."

# Calculate the UTC time based on Pacific time
# During PDT: 4:45 PM PDT = 11:45 PM UTC
# During PST: 4:45 PM PST = 12:45 AM UTC next day
# We'll use 11:45 PM UTC which will be 4:45 PM PDT during daylight saving time
# and 3:45 PM PST during standard time

# Create a new timer file
sudo tee /etc/systemd/system/airbnb-cleaner.timer > /dev/null << EOF
[Unit]
Description=Run Airbnb Cleaning Reminder daily at 4:45 PM Pacific time

[Timer]
OnCalendar=*-*-* 23:45:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd, stop the old timer, and start the new one
sudo systemctl daemon-reload
sudo systemctl stop airbnb-cleaner.timer
sudo systemctl start airbnb-cleaner.timer
sudo systemctl enable airbnb-cleaner.timer

echo "Timer updated successfully!"
echo "The script will now run at 4:45 PM PDT during daylight saving time"
echo "and at 3:45 PM PST during standard time."
echo "To check the timer status, run: systemctl status airbnb-cleaner.timer"
