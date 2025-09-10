#!/bin/bash

echo "🔍 Lead Assessment POC - Diagnostic & Fix Script"
echo "================================================"

# Change to the script directory
cd "$(dirname "$0")"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "❌ Port $port is in use"
        lsof -i :$port
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    echo "🔄 Killing processes on port $port..."
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Function to start backend
start_backend() {
    echo "🔧 Starting backend server..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Load optional .env
    if [ -f .env ]; then
        # shellcheck disable=SC2046
        export $(grep -v '^#' .env | xargs)
    fi
    if [ -n "$GEMINI_API_KEY" ]; then
        echo "🔐 GEMINI_API_KEY detected (masked)"
    else
        echo "ℹ️  GEMINI_API_KEY not set; AI features will use fallback summaries"
    fi
    
    # Start backend
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running
    if curl -s http://127.0.0.1:8000/health > /dev/null; then
        echo "✅ Backend started successfully (PID: $BACKEND_PID)"
        return 0
    else
        echo "❌ Backend failed to start. Check backend.log for details."
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    local port=$1
    echo "🎨 Starting frontend server on port $port..."
    
    cd frontend
    
    # Set port and start
    PORT=$port npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    echo "⏳ Waiting for frontend to start..."
    sleep 15
    
    # Check if frontend is running
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo "✅ Frontend started successfully on port $port (PID: $FRONTEND_PID)"
        cd ..
        return 0
    else
        echo "⚠️  Frontend may still be starting. Check frontend.log for details."
        cd ..
        return 1
    fi
}

# Main diagnostic and fix process
echo "🔍 Step 1: Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 detected: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js detected: $(node --version)"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    echo "✅ npm detected: $(npm --version)"
else
    echo "❌ npm not found"
    exit 1
fi

echo ""
echo "🔍 Step 2: Checking project structure..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo "✅ Frontend directory exists"
else
    echo "❌ Frontend directory not found"
    exit 1
fi

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "🔍 Step 3: Checking port availability..."

# Check backend port
if check_port 8000; then
    echo "✅ Backend port 8000 is available"
else
    echo "🔄 Freeing up port 8000..."
    kill_port 8000
fi

# Check frontend ports
FRONTEND_PORT=""
for port in 3000 3001 3002 3003; do
    if check_port $port; then
        FRONTEND_PORT=$port
        echo "✅ Will use port $port for frontend"
        break
    else
        echo "🔄 Freeing up port $port..."
        kill_port $port
        FRONTEND_PORT=$port
        echo "✅ Will use port $port for frontend"
        break
    fi
done

if [ -z "$FRONTEND_PORT" ]; then
    echo "❌ No available frontend ports found"
    exit 1
fi

echo ""
echo "🚀 Step 4: Starting services..."

# Start backend
if start_backend; then
    echo "✅ Backend is running"
else
    echo "❌ Failed to start backend"
    exit 1
fi

# Start frontend
if start_frontend $FRONTEND_PORT; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend may still be starting"
fi

echo ""
echo "🎉 Step 5: Final status check..."

# Test backend
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
fi

# Test frontend
if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting"
fi

echo ""
echo "📊 Application Status:"
echo "====================="
echo "🔧 Backend: http://127.0.0.1:8000"
echo "📊 Frontend: http://localhost:$FRONTEND_PORT"
echo "📚 API Docs: http://127.0.0.1:8000/docs"
echo "❤️  Health: http://127.0.0.1:8000/health"
echo ""

# Test API endpoints
echo "🧪 Testing API endpoints..."
echo "Health check:"
curl -s http://127.0.0.1:8000/health | head -1
echo ""
echo "Stats endpoint:"
curl -s http://127.0.0.1:8000/api/leads/stats | head -1
echo ""

echo "🌐 Opening application in browser..."
if command -v open &> /dev/null; then
    open http://localhost:$FRONTEND_PORT
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:$FRONTEND_PORT
else
    echo "Please manually open http://localhost:$FRONTEND_PORT in your browser"
fi

echo ""
echo "📝 Logs:"
echo "- Backend: backend.log"
echo "- Frontend: frontend.log"
echo ""
echo "🛑 To stop the application:"
echo "pkill -f uvicorn"
echo "pkill -f 'npm start'"
echo ""
echo "✅ Diagnostic complete!"
