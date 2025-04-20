#!/usr/bin/env python
import datetime
import json
import os
import requests
import sys
import icalendar
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleaning_detailed.log"),
        logging.StreamHandler()
    ]
)

# Constants
PROPERTY_LOCATION = "Austin Bell Unit 310"  # Location the cleaner is familiar with
DEFAULT_RECEIVER = "+14253012277"  # Updated test number


def send_sms(phone_number, message):
    """Send SMS using Twilio API with Account SID and Auth Token authentication."""
    # Load configuration
    config = load_config()
    
    # Get Twilio credentials
    account_sid = config.get('TWILIO_ACCOUNT_SID')
    auth_token = config.get('TWILIO_AUTH_TOKEN')
    twilio_number = config.get('TWILIO_PHONE_NUMBER')
    
    if not account_sid or not auth_token or not twilio_number:
        logging.error("Error: Twilio credentials not configured in config.json")
        return False
    
    try:
        # Import Twilio client
        from twilio.rest import Client
        
        # Create Twilio client using Account SID and Auth Token authentication
        client = Client(account_sid, auth_token)
        
        # Send message
        logging.info(f"Sending SMS to {phone_number} via Twilio")
        message_obj = client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone_number
        )
        
        logging.info(f"Successfully sent SMS to {phone_number}")
        logging.info(f"Message SID: {message_obj.sid}, Status: {message_obj.status}")
        return True
    except ImportError:
        logging.error("Twilio library not installed. Installing now...")
        os.system("pip install twilio")
        return send_sms(phone_number, message)  # Retry after installation
    except Exception as e:
        logging.error(f"Error sending SMS: {e}")
        return False


def load_config():
    """Load configuration from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            # Mask sensitive information in logs
            masked_config = {k: '***' if k in ['D7_API_TOKEN', 'TWILIO_AUTH_TOKEN'] else v for k, v in config.items()}
            logging.info(f"Loaded configuration: {json.dumps(masked_config)}")
            return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}


def check_checkout_tomorrow(dry_run=False):
    """Checks for events ending tomorrow and notifies cleaner.
    
    Assumptions:
    - In Airbnb's iCal format, DTEND is the date the guest checks out
    - DTSTART is the date the guest checks in
    - We directly use these dates without additional processing
    
    Args:
        dry_run: If True, don't actually send SMS, just print what would be sent
    """
    # Load configuration
    config = load_config()
    
    # Get cleaner's phone number (use default if not configured)
    cleaner_phone = config.get('CLEANER_PHONE', DEFAULT_RECEIVER)
    
    if not cleaner_phone:
        logging.error("Error: Cleaner's phone number not configured in config.json")
        return
    
    # Get iCal URL
    ical_url = config.get('ICAL_URL')
    
    if not ical_url:
        logging.error("Error: iCal URL not configured in config.json")
        return
    
    # Get property location
    property_location = config.get('PROPERTY_LOCATION', PROPERTY_LOCATION)
    
    # Get tomorrow's date
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    logging.info(f"Checking for events ending tomorrow ({tomorrow})")
    
    try:
        # Download iCal data
        logging.info(f"Downloading iCal data from: {ical_url}")
        response = requests.get(ical_url, verify=False)  # Note: verify=False is not recommended for production
        
        if response.status_code != 200:
            logging.error(f"Failed to download iCal data. Status code: {response.status_code}")
            return
        
        # Parse iCal data
        cal = icalendar.Calendar.from_ical(response.text)
        
        # Check for events ending tomorrow
        found_event = False
        next_checkin_date = None
        
        # First, find the next check-in after tomorrow
        for component in cal.walk():
            if component.name == "VEVENT":
                start_date = component.get('dtstart').dt
                if isinstance(start_date, datetime.datetime):
                    start_date = start_date.date()
                
                if start_date > tomorrow and (next_checkin_date is None or start_date < next_checkin_date):
                    next_checkin_date = start_date
        
        # Now check for events ending tomorrow
        for component in cal.walk():
            if component.name == "VEVENT":
                end_date = component.get('dtend').dt
                if isinstance(end_date, datetime.datetime):
                    end_date = end_date.date()
                
                if end_date == tomorrow:
                    found_event = True
                    summary = component.get('summary')
                    logging.info(f"Found event ending tomorrow: {summary}, End date: {end_date}")
                    
                    # Format the message
                    tomorrow_day = tomorrow.strftime("%A, %B %d, %Y")
                    
                    message = f"Cleaning needed tomorrow ({tomorrow_day}) at {property_location}."
                    
                    if next_checkin_date:
                        days_until_checkin = (next_checkin_date - tomorrow).days
                        next_checkin_day = next_checkin_date.strftime("%A, %B %d")
                        
                        if days_until_checkin == 1:
                            message += f" Next check-in is the day after tomorrow ({next_checkin_day})."
                        else:
                            message += f" Next check-in is in {days_until_checkin} days ({next_checkin_day})."
                    
                    if dry_run:
                        logging.info(f"[DRY RUN] Would send SMS: {message}")
                    else:
                        # Send SMS
                        send_sms(cleaner_phone, message)
        
        if not found_event:
            logging.info("No events ending tomorrow.")
    
    except Exception as e:
        logging.error(f"Error checking for events: {e}")


def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Airbnb Cleaner Notification')
    parser.add_argument('--dry-run', action='store_true', help='Do not send SMS, just print what would be sent')
    parser.add_argument('--test-sms', action='store_true', help='Send a test SMS to the cleaner')
    args = parser.parse_args()
    
    if args.test_sms:
        # Get cleaner's phone number
        config = load_config()
        cleaner_phone = config.get('CLEANER_PHONE', DEFAULT_RECEIVER)
        
        if not cleaner_phone:
            logging.error("Error: Cleaner's phone number not configured in config.json")
            return
        
        logging.info(f"Sending test SMS to {cleaner_phone}")
        send_sms(cleaner_phone, "This is a test message from the Airbnb cleaning reminder system.")
        logging.info("Test SMS sent successfully")
    else:
        # Check for events ending tomorrow
        check_checkout_tomorrow(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
