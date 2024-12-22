#!/bin/bash

VENV_DIR="/home/ec2-user/C-3PO/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

python3 -m pip install -r requirements.txt

while true
do
    echo "Starting bot..."
    python3 main.py
    echo "Bot crashed with exit code $?. Restarting in 5 seconds..."
    sleep 5
done
