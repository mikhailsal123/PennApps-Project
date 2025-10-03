#!/bin/bash

# Start Flask backend in background
python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Next.js frontend (this will be the main process)
cd frontend && npm start
