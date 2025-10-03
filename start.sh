#!/bin/bash

# Start Flask backend in background
python3 app.py &

# Start Next.js frontend
cd frontend && npm start
