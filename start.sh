#!/bin/bash

python3 -m pip install -r requirements.txt

while true
do
    echo "Starting bot..."
    python3 main.py
    echo "Bot crashed with exit code $?. Restarting in 5 seconds..."
    sleep 5
done
