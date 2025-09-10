#!/bin/bash

echo "========================================"
echo "   Lead Assessment POC - Starting App"
echo "========================================"
echo

# Change to the script directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ and try again"
    exit 1
fi

echo "✓ Python and Node.js detected"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

echo "✓ Virtual environment ready"
echo

# Install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi

echo "✓ Python dependencies installed"
echo

# Load environment variables if present
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs)
fi

FAST_START=${FAST_START:-false}
SKIP_TRAIN=${SKIP_TRAIN:-false}

if [ "$FAST_START" = "true" ] || [ "$FAST_START" = "1" ]; then
    echo "FAST_START enabled: skipping data generation & model training (mock predictions will be used)"
else
    if [ "$SKIP_TRAIN" = "true" ] || [ "$SKIP_TRAIN" = "1" ]; then
        echo "SKIP_TRAIN enabled: skipping model training"
    else
        echo "Generating sample data and training models..."
        python data_generator.py || echo "WARNING: Failed to generate sample data"
        python ml_models.py || echo "WARNING: Failed to train models"
        echo "✓ Data and models ready"
    fi
fi
echo

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Node.js dependencies"
    exit 1
fi

echo "✓ Node.js dependencies installed"
echo

# Start backend in background
echo "Starting backend server..."
cd ..
source venv/bin/activate
API_PORT_RUN=${API_PORT:-8000}
echo "Backend will listen on port ${API_PORT_RUN}"
if [ -n "$GEMINI_API_KEY" ]; then
    echo "Gemini API key detected (masked)"
else
    echo "Gemini API key not set; AI summaries will be fallback"
fi
python -m uvicorn backend.main:app --host 127.0.0.1 --port "$API_PORT_RUN" > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -s "http://127.0.0.1:${API_PORT_RUN}/health" > /dev/null; then
    echo "WARNING: Backend may not have started properly"
fi

# Start frontend in background
echo "Starting frontend server..."
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 10

echo
echo "========================================"
echo "   Application Started Successfully!"
echo "========================================"
echo
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API Docs: http://localhost:${API_PORT_RUN}/docs"
echo "❤️  Health Check: http://localhost:${API_PORT_RUN}/health"
echo
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo
echo "Logs:"
echo "- Backend: backend.log"
echo "- Frontend: frontend.log"
echo
echo "$BACKEND_PID" > .app_backend.pid
echo "$FRONTEND_PID" > .app_frontend.pid


# Open the dashboard in the default browser
echo "Opening dashboard in your browser..."
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
else
    echo "Please manually open http://localhost:3000 in your browser"
fi

echo
echo "To stop the application, run:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo
echo "Or press Ctrl+C to stop this script and the servers"
echo

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    rm -f .app_backend.pid .app_frontend.pid
    echo "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Press Ctrl+C to stop the application..."
wait