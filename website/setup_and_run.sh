#!/bin/bash

echo "================================"
echo "PDF Text Extractor Setup Script"
echo "================================"
echo

echo "Installing Backend Dependencies..."
cd backend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to install backend dependencies"
    exit 1
fi

echo
echo "Installing Frontend Dependencies..."
cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to install frontend dependencies"
    exit 1
fi

echo
echo "Installing Python Dependencies..."
cd ../../text-extractor
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install Python dependencies"
    exit 1
fi

echo
echo "================================"
echo "Setup Complete! Starting servers..."
echo "================================"
echo

cd ../website

echo "Starting Backend Server..."
cd backend
npm start &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting Frontend Server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo
echo "================================"
echo "Servers are running!"
echo "================================"
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait