#!/bin/bash

# Start Flask backend in background on port 5000
PORT=5000 python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start Next.js frontend on port 3000
cd frontend
npm start
