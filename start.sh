#!/bin/bash

echo "🌍 Starting CarbonBuddy..."
echo ""

# Kill existing processes on ports 8000 and 3000
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load environment variables from .env file if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

# Check if DEDALUS_API_KEY is set
if [ -z "$DEDALUS_API_KEY" ]; then
    echo "⚠️  WARNING: DEDALUS_API_KEY not set!"
    echo "Please set it with: export DEDALUS_API_KEY='your-key-here'"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "🔧 Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "⚠️  Warning: Virtual environment not found. Python dependencies may not be available."
fi

# Start backend
echo "📡 Starting backend on http://localhost:8000..."
cd "$SCRIPT_DIR/backend"
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000..."
cd "$SCRIPT_DIR/frontend"
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ CarbonBuddy is running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "   Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
