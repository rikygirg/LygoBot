#!/bin/bash

# List all screen sessions with the name "bot" and extract session IDs
sessions=$(screen -ls | grep "bot" | awk '{print $1}')

# Loop through each session ID and kill it
for session_id in $sessions; do
    screen -S $session_id -X quit
done


# Path to the virtual environment activation script
VENV_ACTIVATE_PATH="PATH_TO_VENV/bin/activate"

# Start a new detached screen session named "bot" and execute the following commands inside it
screen -dmS bot bash -c " \
    # Activate the virtual environment
    source $VENV_ACTIVATE_PATH; \
    \
    # Run the main.py file
    python3 PATH_TO_BOT_LYGO/main.py; \
    \
    # Keep the screen session open after the script finishes
    exec bash"
