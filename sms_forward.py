#!/usr/bin/env python
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
from twilio.rest import Client

app = Flask(__name__)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming SMS messages and forward them to your personal number"""
    # Get the message the user sent our Twilio number
    incoming_message = request.values.get('Body', '')
    # Get the number the message was sent from
    from_number = request.values.get('From', '')
    
    # Load config
    config = load_config()
    
    # Get Twilio credentials
    account_sid = config.get('TWILIO_ACCOUNT_SID')
    auth_token = config.get('TWILIO_AUTH_TOKEN')
    twilio_number = config.get('TWILIO_PHONE_NUMBER')
    
    # Your personal number to forward to
    your_personal_number = config.get('PERSONAL_PHONE', '+14253012277')  # Default to the cleaner number if not set
    
    # Create Twilio client
    client = Client(account_sid, auth_token)
    
    # Forward the message to your personal number
    client.messages.create(
        body=f"From: {from_number}\n\n{incoming_message}",
        from_=twilio_number,
        to=your_personal_number
    )
    
    # Create a response
    resp = MessagingResponse()
    
    # You can add a reply message if you want the sender to get an auto-response
    # resp.message("Thanks for your message! It has been forwarded.")
    
    return str(resp)

if __name__ == "__main__":
    # Run the Flask app when this file is executed directly
    app.run(debug=True, host='0.0.0.0', port=5000)
