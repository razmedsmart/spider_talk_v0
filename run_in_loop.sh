#!/bin/bash

# Replace 'your_program' with the actual program you want to run.
PROGRAM="./spider.sh"

# Function to handle SIGINT (Ctrl+C)
cleanup() {
    echo -e "\nCaught Ctrl+C, exiting."
    exit 0
}

# Trap SIGINT and call the cleanup function
trap cleanup SIGINT

# Check if the program exists and is executable
if ! [ -x "$(command -v $PROGRAM)" ]; then
    echo "Error: $PROGRAM is not installed or not executable." >&2
    exit 1
fi

# Run the program in an infinite loop
while true; do
    ./$PROGRAM
    echo "Program completed. Restarting..."
done
