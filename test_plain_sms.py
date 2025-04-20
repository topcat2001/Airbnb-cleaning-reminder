#!/usr/bin/env python
import json
import requests

def load_config():
    """Load configuration from config.json file."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def send_plain_sms():
    """Send a very simple SMS message without any special formatting."""
    # Load configuration
    config = load_config()
    
    # Get API token and phone number
    api_token = config.get('D7_API_TOKEN')
    phone_number = config.get('CLEANER_PHONE')
    
    if not api_token:
        print("Error: D7 SMS API token not configured in config.json")
        return False
        
    if not phone_number:
        print("Error: Cleaner's phone number not configured in config.json")
        return False
    
    # Prepare the request
    url = "https://api.d7networks.com/messages/v1/send"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    message = "Hello, this is a test message. Please reply if you receive this."
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
            "originator": "Karthik",
            "report_url": "https://the_url_to_receive_delivery_report.com"
        }
    }
    
    try:
        # Send the request
        print(f"Sending SMS to {phone_number}")
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully sent SMS to {phone_number}")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Failed to send SMS. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

if __name__ == "__main__":
    send_plain_sms()
