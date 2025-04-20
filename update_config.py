#!/usr/bin/env python
import json
import os

# Path to config file
config_path = 'config.json'

# Read the current config
with open(config_path, 'r') as f:
    config = json.load(f)

# Update the phone number
old_phone = config.get('CLEANER_PHONE', '')
config['CLEANER_PHONE'] = '+12068011818'

# Write the updated config back
with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

print(f"Updated phone number from {old_phone} to {config['CLEANER_PHONE']}")
