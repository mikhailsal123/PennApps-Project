#!/bin/bash

# Start Flask backend in background on port 5000
PORT=5000 python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Install Next.js dependencies and start frontend
cd frontend
npm install
PORT=3000 npm start
