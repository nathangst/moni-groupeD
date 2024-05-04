#!/bin/bash

# Chemin vers votre script Python
SCRIPT_PATH="/usr/local/bin/rsyslog_discord.py"

while IFS= read -r line; do
    echo "$line" | python3 "$SCRIPT_PATH"
done
