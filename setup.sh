#!/bin/bash

# Lead Assessment POC - Team Setup Script
echo "🚀 Setting up Lead Assessment POC for team..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create environment file
echo "⚙️ Creating environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Created .env file from template. Please update with your API keys."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your API keys (especially GEMINI_API_KEY)"
echo "2. Run: ./start_app.sh (macOS/Linux) or start_app.bat (Windows)"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Documentation:"
echo "- README.md - Project overview"
echo "- ARCHITECTURE.md - System architecture"
echo "- DEPLOYMENT.md - Deployment guide"
echo "- RUNTIME_GUIDE.md - Runtime instructions"
echo ""
echo "🆘 Need help? Check the documentation or contact the team."
