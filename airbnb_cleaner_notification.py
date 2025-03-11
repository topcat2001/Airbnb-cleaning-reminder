#!/usr/bin/env python
import datetime
import json
import os
import requests
import sys
import icalendar

# Constants
PROPERTY_LOCATION = "Austin Bell Unit 310"  # Location the cleaner is familiar with

def send_sms(phone_number, message):
    """Send SMS using D7 SMS API with API token authentication."""
    # Load configuration
    config = load_config()
    
    # Get API token
    api_token = config.get('D7_API_TOKEN')
    
    if not api_token:
        print("Error: D7 SMS API token not configured in config.json")
        return False
    
    # Prepare the request
    url = "https://api.d7networks.com/messages/v1/send"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    data = {
        "messages": [
            {
                "channel": "sms",
                "recipients": [phone_number],
                "content": message,
                "msg_type": "text",
                "data_coding": "text"
            }
        ],
        "message_globals": {
            "originator": "AirbnbClean",
            "report_url": "https://the_url_to_receive_delivery_report.com"
        }
    }
    
    try:
        # Send the request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        if response.status_code in [200, 201, 202]:
            print(f"Successfully sent SMS to {phone_number}")
            return True
        else:
            print(f"Failed to send SMS. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def load_config():
    """Load configuration from config.json file."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        default_config = {
            "D7_API_TOKEN": "",
            "CLEANER_PHONE": "",
            "ICAL_URL": "",
            "PROPERTY_LOCATION": "Austin Bell Unit 310"
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file at {config_path}. Please update with your credentials.")
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def check_checkout_tomorrow():
    """Checks for events ending tomorrow and notifies cleaner.
    
    Assumptions:
    - In Airbnb's iCal format, DTEND is the date the guest checks out
    - DTSTART is the date the guest checks in
    - We directly use these dates without additional processing
    """
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Check for Airbnb checkouts tomorrow')
    parser.add_argument('--dry-run', action='store_true', help='Do not send SMS, just print what would be sent')
    args, unknown = parser.parse_known_args()
    
    # Load configuration
    config = load_config()
    
    # Check if cleaner's phone is configured
    cleaner_phone = config.get('CLEANER_PHONE')
    if not cleaner_phone:
        print("Error: Cleaner's phone number not configured in config.json")
        return
    
    # Get today's date and tomorrow's date
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    
    print(f"Checking for events ending tomorrow ({tomorrow.isoformat()})")
    
    # Get iCal URL from config
    ical_url = config.get('ICAL_URL')
    
    # Check if the iCal URL is valid
    if not ical_url or not (ical_url.startswith('http://') or ical_url.startswith('https://')):
        print("Error: iCal URL is not valid")
        print("Please update your config.json with a valid Airbnb iCal URL")
        return
        
    try:
        # Download the iCal file
        print(f"Downloading iCal data from: {ical_url}")
        response = requests.get(ical_url, verify=False)
        ical_data = response.content
        
        # Parse the iCal data
        calendar = icalendar.Calendar.from_ical(ical_data)
        
        # Process all events
        checkout_events = []
        all_events = []
        
        # First collect all events
        for component in calendar.walk():
            if component.name == "VEVENT":
                summary = str(component.get('SUMMARY', 'No Title'))
                start_date = component.get('DTSTART').dt
                end_date = component.get('DTEND').dt
                
                # Convert to date if datetime
                if isinstance(start_date, datetime.datetime):
                    start_date = start_date.date()
                if isinstance(end_date, datetime.datetime):
                    end_date = end_date.date()
                
                # Store event info
                event_info = {
                    'summary': summary,
                    'start': start_date,
                    'end': end_date
                }
                all_events.append(event_info)
                
                # Check if this event ends tomorrow (checkout)
                if end_date == tomorrow and 'reserved' in summary.lower():
                    checkout_events.append(event_info)
                    print(f"Found event ending tomorrow: {summary}, End date: {end_date}")
        
        # If we found events ending tomorrow, send notification
        if checkout_events:
            # Look for upcoming events starting in the next 3 days
            next_checkin = None
            three_days_later = tomorrow + datetime.timedelta(days=3)
            
            for event in all_events:
                # Only consider 'Reserved' events
                if 'reserved' not in event['summary'].lower():
                    continue
                
                # Check if this is a future check-in within the next 3 days
                if (event['start'] >= tomorrow and 
                    event['start'] <= three_days_later):
                    
                    # If we haven't found a check-in yet, or this one is earlier
                    if next_checkin is None or event['start'] < next_checkin['start']:
                        next_checkin = event
            
            # Prepare the message
            message = f"Cleaning needed tomorrow ({tomorrow.strftime('%A, %B %d, %Y')}) at {PROPERTY_LOCATION}."
            
            # Add next check-in information if found
            if next_checkin:
                days_until = (next_checkin['start'] - tomorrow).days
                
                if days_until == 1:
                    message += f" Next check-in is the day after tomorrow ({next_checkin['start'].strftime('%A, %B %d')})."
                else:
                    message += f" Next check-in is on {next_checkin['start'].strftime('%A, %B %d')}."
            else:
                message += " No upcoming check-ins in the next 3 days."
            
            # Send the message
            if not args.dry_run:
                if send_sms(cleaner_phone, message):
                    print(f"Successfully sent SMS notification: {message}")
                else:
                    print("Failed to send SMS notification")
            else:
                print(f"[DRY RUN] Would send SMS: {message}")
        else:
            print(f"No events ending tomorrow ({tomorrow.isoformat()}) at {PROPERTY_LOCATION}")
            
    except Exception as e:
        print(f"Error checking calendar: {e}")

def main():
    """Main function to run the script."""
    check_checkout_tomorrow()

if __name__ == "__main__":
    main()
