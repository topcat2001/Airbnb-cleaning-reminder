# SMS Forwarding Setup for Twilio

## Overview
This guide explains how to set up automatic forwarding of SMS messages received by your Twilio number to your personal cell phone.

## Option 1: Using TwiML Bin (Easiest)

1. **Log in to your Twilio Console** at https://www.twilio.com/console

2. **Create a TwiML Bin**:
   - Navigate to Runtime → TwiML Bins
   - Click "Create new TwiML Bin"
   - Give it a friendly name like "SMS Forwarding"
   - Paste the following code (replace with your personal number):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
     <Message to="+14253012277">
       From: {{From}}
       
       {{Body}}
     </Message>
   </Response>
   ```
   - Save the TwiML Bin

3. **Configure your Twilio Phone Number**:
   - Go to Phone Numbers → Manage → Active Numbers
   - Select your Twilio number (+12062229114)
   - Under "Messaging", set the webhook for "A MESSAGE COMES IN" to point to your TwiML Bin URL
   - Save your changes

## Option 2: Using a Custom Flask Application

For more control, you can use the `sms_forward.py` script included in this repository.

1. **Install required packages**:
   ```
   pip install flask twilio
   ```

2. **Update your config.json** to include your personal phone number:
   ```json
   "PERSONAL_PHONE": "+14253012277"
   ```

3. **Deploy the Flask application** to your Azure server or another hosting service.

4. **Configure your Twilio Phone Number**:
   - Go to Phone Numbers → Manage → Active Numbers
   - Select your Twilio number (+12062229114)
   - Under "Messaging", set the webhook for "A MESSAGE COMES IN" to point to your deployed Flask app URL (e.g., https://your-server.com/sms)
   - Save your changes

## Testing the Forwarding

To test that forwarding is working correctly:

1. Send a text message to your Twilio number (+12062229114)
2. You should receive the forwarded message on your personal phone shortly after

## Notes

- Message forwarding happens in near real-time
- Standard SMS rates apply for forwarded messages
- You can customize the format of forwarded messages in either the TwiML Bin or the Flask application
