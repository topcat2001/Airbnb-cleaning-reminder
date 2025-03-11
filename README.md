# Airbnb Cleaning Reminder

This Python application automatically checks your Airbnb iCal feed for bookings that end tomorrow and sends an SMS notification to your cleaner using the D7 SMS API. It also includes information about the next upcoming check-in.

## Setup Instructions

### 1. Get Your Airbnb iCal URL

1. Log in to your Airbnb account
2. Go to your listing's calendar
3. Click on "Export Calendar" (usually found in the calendar settings)
4. Copy the iCal URL provided by Airbnb

### 2. Configure the Application

When you first run the application, it will create a `config.json` file with default settings. You'll need to edit this file to add your specific information:

```json
{
    "ICAL_URL": "https://www.airbnb.com/calendar/ical/YOUR_LISTING_ID.ics?s=YOUR_SECRET_KEY",
    "CLEANER_PHONE": "+1234567890",  # Replace with your cleaner's phone number
    "D7_API_TOKEN": "your_d7_api_token",  # Get this from your D7 Networks account
    "PROPERTY_LOCATION": "Austin Bell Unit 310"  # Property location (cleaner is familiar with this location)
}
```

- `ICAL_URL`: Your Airbnb listing's iCal URL
- `CLEANER_PHONE`: Your cleaner's phone number in international format (e.g., +1234567890)
- `D7_API_TOKEN`: Your D7 Networks API token (get this from your D7 Networks account)
- `PROPERTY_LOCATION`: The property location as known to your cleaner (e.g., "Austin Bell Unit 310" - your cleaner is already familiar with this location)

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

Normal mode:
```bash
python airbnb_cleaner_notification.py
```

Dry run mode (no SMS sent):
```bash
python airbnb_cleaner_notification.py --dry-run
```

Test with a specific date:
```bash
python airbnb_cleaner_notification.py --dry-run --test-date YYYY-MM-DD
```

The application will:
1. Check your Airbnb calendar for any bookings ending tomorrow
2. If a checkout is found, send an SMS to your cleaner with:
   - The property location
   - The checkout date
   - Information about the next check-in (if any)

## Example SMS Message

```
Cleaning needed tomorrow (Wednesday, March 12, 2025) at Austin Bell Unit 310. Next check-in is the day after tomorrow (Thursday, March 13).
```

## Automating with Cron

To run this script automatically every day, you can set up a cron job:

1. Open your crontab file:
   ```bash
   crontab -e
   ```

2. Add a line to run the script daily (e.g., at 9 AM):
   ```
   0 9 * * * cd /path/to/Airbnb\ cleaning\ reminder && /usr/bin/python airbnb_cleaner_notification.py >> cleaning_log.txt 2>&1
   ```

## Troubleshooting

- Check that your Airbnb iCal URL is valid and accessible
- Verify that your D7 SMS API credentials are correct
- Make sure your cleaner's phone number is in the correct international format
- Review the console output or log file for any error messages
- Use the `--dry-run` flag to test the script without sending SMS messages
- Use the `--test-date` option with `--dry-run` to test specific dates
