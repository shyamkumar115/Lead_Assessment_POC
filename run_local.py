#!/usr/bin/env python3
"""
Local Development Runner for Lead Assessment POC
This script sets up and runs the application locally for development
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, cwd=cwd, shell=shell, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def check_node_version():
    """Check if Node.js is installed"""
    result = run_command("node --version")
    if result:
        print(f"✓ Node.js {result.strip()} detected")
        return True
    else:
        print("Error: Node.js is not installed. Please install Node.js 16 or higher")
        return False

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command("python -m venv venv")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print("Installing Python dependencies...")
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Generate sample data
    print("Generating sample data...")
    run_command(f"{python_cmd} data_generator.py")
    
    # Train models
    print("Training ML models...")
    run_command(f"{python_cmd} ml_models.py")
    
    print("✓ Backend setup complete")

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("Error: Frontend directory not found")
        return False
    
    # Install npm dependencies
    print("Installing npm dependencies...")
    result = run_command("npm install", cwd=frontend_dir)
    if not result:
        return False
    
    print("✓ Frontend setup complete")
    return True

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        python_cmd = "venv/bin/python"
    
    # Start backend in background
    backend_process = subprocess.Popen([
        python_cmd, "-m", "uvicorn", "backend.main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    
    # Wait for backend to start
    time.sleep(5)
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend server started successfully")
            return backend_process
    except:
        pass
    
    print("⚠️  Backend server may not be fully ready yet")
    return backend_process

def start_frontend():
    """Start the frontend development server"""
    print("\n🚀 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    
    # Start frontend in background
    frontend_process = subprocess.Popen([
        "npm", "start"
    ], cwd=frontend_dir)
    
    # Wait for frontend to start
    time.sleep(10)
    
    print("✓ Frontend server started successfully")
    return frontend_process

def main():
    """Main function to set up and run the application"""
    print("🎯 Lead Assessment POC - Local Development Setup")
    print("=" * 50)
    
    # Check prerequisites
    check_python_version()
    if not check_node_version():
        sys.exit(1)
    
    # Set up environments
    setup_backend()
    if not setup_frontend():
        sys.exit(1)
    
    # Start servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    print("\n🎉 Application is starting up!")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:3000")
    print("🔧 API Docs: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop all servers")
    
    # Open browser
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✓ Servers stopped")

if __name__ == "__main__":
    main()
