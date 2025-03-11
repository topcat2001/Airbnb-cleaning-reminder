#!/usr/bin/env python
import sys
import datetime
import json
import requests
import icalendar
from unittest.mock import patch

# Create a simplified version of our check_checkout_tomorrow function for testing
def test_checkout_logic(today_date, ical_data):
    """Test the checkout logic with a specific date and iCal data"""
    print(f"Testing with today's date: {today_date.isoformat()}")
    tomorrow = today_date + datetime.timedelta(days=1)
    print(f"Checking for events ending tomorrow: {tomorrow.isoformat()}")
    
    # Parse the iCal data
    calendar = icalendar.Calendar.from_ical(ical_data)
    
    # Process all events
    checkout_events = []
    all_events = []
    
    # First collect all events
    print("\nAll events in calendar:")
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
            
            # Print all events
            print(f"Event: {summary}, Start: {start_date}, End: {end_date}")
            
            # Check if this event ends tomorrow (checkout)
            if end_date == tomorrow and 'reserved' in summary.lower():
                checkout_events.append(event_info)
                print(f"  --> Found event ending tomorrow: {summary}, Start: {start_date}, End: {end_date}")
    
    # If we found events ending tomorrow, prepare notification
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
        message = f"Cleaning needed tomorrow ({tomorrow.strftime('%A, %B %d, %Y')}) at Austin Bell Unit 310."
        
        # Add next check-in information if found
        if next_checkin:
            days_until = (next_checkin['start'] - tomorrow).days
            
            if days_until == 1:
                message += f" Next check-in is the day after tomorrow ({next_checkin['start'].strftime('%A, %B %d')})."
            else:
                message += f" Next check-in is on {next_checkin['start'].strftime('%A, %B %d')}."
        else:
            message += " No upcoming check-ins in the next 3 days."
        
        print(f"Would send SMS: {message}")
    else:
        print(f"No events ending tomorrow ({tomorrow.isoformat()}) at Austin Bell Unit 310")

# Real iCal data from Airbnb
mock_ical_data = '''BEGIN:VCALENDAR
PRODID:-//Airbnb Inc//Hosting Calendar 1.0//EN
CALSCALE:GREGORIAN
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:20250309T114927Z
DTSTART;VALUE=DATE:20250304
DTEND;VALUE=DATE:20250309
SUMMARY:Reserved
UID:1418fb94e984-7ae3da5a502f8a9185ed4c15c5b148a3@airbnb.com
DESCRIPTION:Reservation URL: https://www.airbnb.com/hosting/reservations/de
 tails/HMSPY4Q5SZ
Phone Number (Last 4 Digits): 3658
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20250309T114927Z
DTSTART;VALUE=DATE:20250310
DTEND;VALUE=DATE:20250312
SUMMARY:Reserved
UID:1418fb94e984-ae199852f5dfa351a2c858a696e0869c@airbnb.com
DESCRIPTION:Reservation URL: https://www.airbnb.com/hosting/reservations/de
 tails/HM9STJ4WM4
Phone Number (Last 4 Digits): 0775
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20250309T114927Z
DTSTART;VALUE=DATE:20250313
DTEND;VALUE=DATE:20250315
SUMMARY:Reserved
UID:1418fb94e984-2bfbd274ea63c5658b5e0bb9a46b221a@airbnb.com
DESCRIPTION:Reservation URL: https://www.airbnb.com/hosting/reservations/de
 tails/HMJE9NK2QJ
Phone Number (Last 4 Digits): 2910
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20250309T114927Z
DTSTART;VALUE=DATE:20250315
DTEND;VALUE=DATE:20250317
SUMMARY:Reserved
UID:1418fb94e984-6f9859846bc1147ba8b6bcbb79af63dc@airbnb.com
DESCRIPTION:Reservation URL: https://www.airbnb.com/hosting/reservations/de
 tails/HMWW5JZS9A
Phone Number (Last 4 Digits): 6976
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20250309T114927Z
DTSTART;VALUE=DATE:20250318
DTEND;VALUE=DATE:20250321
SUMMARY:Reserved
UID:1418fb94e984-4c56389ca75d8727d8f88b944cee2887@airbnb.com
DESCRIPTION:Reservation URL: https://www.airbnb.com/hosting/reservations/de
 tails/HMZYMEKS9P
Phone Number (Last 4 Digits): 8431
END:VEVENT
END:VCALENDAR
'''

# Define test dates
test_dates = [
    datetime.date(2025, 3, 9),   # Testing for March 10 checkout (none)
    datetime.date(2025, 3, 10),  # Testing for March 11 checkout (none)
    datetime.date(2025, 3, 11),  # Testing for March 12 checkout (found)
    datetime.date(2025, 3, 12),  # Testing for March 13 checkout (none)
    datetime.date(2025, 3, 13),  # Testing for March 14 checkout (none)
    datetime.date(2025, 3, 14),  # Testing for March 15 checkout (found)
]

# Run tests for each date
for test_date in test_dates:
    print(f"\n===== TESTING FOR {test_date.strftime('%A, %B %d, %Y')} =====\n")
    test_checkout_logic(test_date, mock_ical_data)
    print("\n===== END TEST =====\n")

print("All tests complete. This shows what the notification messages would be for each date.")
