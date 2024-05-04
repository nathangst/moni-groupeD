#!/usr/bin/env python3
import requests
import sys

WEBHOOK_URL = "https://discord.com/api/webhooks/1221823200103759932/eGpzOaipTRTNTM5kI1z-ZfkjGwM1f37excK-zXwoBIPQoooJWn-N7yARbqEBaELOke7p"


def send_to_discord(message):
    data = {"content": message.strip()}  # Strip any leading/trailing whitespace
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}", file=sys.stderr)

if __name__ == "__main__":
    # Read the message from stdin
    message = sys.stdin.read().strip()  # Strip any leading/trailing whitespace
    if message:  # Ensure message is not empty
        send_to_discord(message)
    else:
        print("Error: Empty message received", file=sys.stderr)
                                                                  
