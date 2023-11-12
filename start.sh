#!/bin/bash
until python3 main.py; do
    echo "The bot crashed with exit code $?. Restarting..." >&2
    sleep 1
done
