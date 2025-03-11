#!/usr/bin/env python
import json
import os
import requests

def load_config():
    """Load configuration from config.json file."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def print_raw_ical_data():
    # Load configuration
    config = load_config()
    
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
        ical_data = response.content.decode('utf-8')
        
        # Print the raw iCal data
        print("\nRAW ICAL DATA:")
        print("==============")
        print(ical_data)
        print("==============")
        
    except Exception as e:
        print(f"Error downloading iCal data: {e}")

if __name__ == "__main__":
    print_raw_ical_data()
