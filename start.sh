#!/bin/bash

# Start the server
# python ./src/main.py

inotifywait -m ./src -e close_write | while read path action file; do
    if [[ "$file" =~ \.py$ ]]; then
        echo "Restarting server due to Python file change..."
        pkill -f main.py
        python ./src/main.py &
    fi
done