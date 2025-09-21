#!/bin/bash

# Start both Flask backend and Next.js frontend
echo "Starting PennApps Trading Platform..."

# Function to kill background processes on script exit
cleanup() {
    echo "Shutting down applications..."
    kill $FLASK_PID $NEXT_PID 2>/dev/null
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Flask backend
echo "Starting Flask backend on port 5002..."
cd /Users/michaelsaleev/PennApps-Project
python app.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

# Start Next.js frontend
echo "Starting Next.js frontend on port 3000..."
cd /Users/michaelsaleev/PennApps-Project/frontend
npm run dev &
NEXT_PID=$!

echo "Both applications are starting..."
echo "Flask backend: http://localhost:5002"
echo "Next.js frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both applications"

# Wait for both processes
wait
