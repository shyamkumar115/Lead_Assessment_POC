# 🚀 **Lead Assessment POC - VS Code Runtime Guide**

## **📋 Prerequisites**

### **Required Software**
- **VS Code** with Python and JavaScript extensions
- **Python 3.8+** (recommended: Python 3.11+)
- **Node.js 16+** (recommended: Node.js 18+)
- **Git** (for version control)

### **VS Code Extensions**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "ms-vscode.vscode-json",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

---

## **🔧 Initial Setup**

### **1. Clone & Open Project**
```bash
# Open VS Code in project directory
code /Users/shyamkumar/Desktop/New_Relic_Projects/work/projects/Lead_Assessment_POC
```

### **2. Python Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### **3. Node.js Dependencies**
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

---

## **⚙️ VS Code Configuration**

### **1. Create `.vscode/settings.json`**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true
  }
}
```

### **2. Create `.vscode/launch.json`**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Backend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "env": {
        "GEMINI_API_KEY": "<your_gemini_api_key>"
      },
      "args": ["--host", "0.0.0.0", "--port", "8001", "--reload"]
    }
  ]
}
```

### **3. Create `.vscode/tasks.json`**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend Server",
      "type": "shell",
      "command": "source venv/bin/activate && GEMINI_API_KEY='<your_gemini_api_key>' python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "problemMatcher": []
    },
    {
      "label": "Start Frontend Server",
      "type": "shell",
      "command": "cd frontend && PORT=3002 npm start",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "problemMatcher": []
    }
  ]
}
```

---

## **🎯 Running the Application**

### **Method 1: VS Code Tasks (Recommended)**

#### **Step 1: Start Backend**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select "Start Backend Server"
4. Wait for "Application startup complete" message

#### **Step 2: Start Frontend**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select "Start Frontend Server"
4. Wait for "webpack compiled" message

### **Method 2: Integrated Terminal**

#### **Terminal 1 - Backend**
```bash
# Activate virtual environment
source venv/bin/activate

# Start backend server
GEMINI_API_KEY='<your_gemini_api_key>' python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

#### **Terminal 2 - Frontend**
```bash
# Navigate to frontend
cd frontend

# Start frontend server
PORT=3002 npm start
```

### **Method 3: VS Code Debugger**

#### **Backend Debugging**
1. Set breakpoints in `backend/main.py`
2. Press `F5` or go to Run → Start Debugging
3. Select "Launch Backend" configuration
4. Debug with full VS Code debugging features

---

## **🌐 Accessing the Application**

### **Frontend Application**
- **URL**: http://localhost:3002
- **Features**: Full GTM Intelligence Dashboard

### **Backend API**
- **Base URL**: http://localhost:8001
- **Health Check**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs (Swagger UI)

---

## **🔍 Development Workflow**

### **1. Backend Development**
```bash
# Make changes to backend/main.py
# Server auto-reloads with --reload flag
# Check terminal for any errors
```

### **2. Frontend Development**
```bash
# Make changes to frontend/src/
# Hot reload automatically updates browser
# Check browser console for errors
```

### **3. API Testing**
```bash
# Test backend endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/leads?limit=5
```

---

## **🐛 Troubleshooting**

### **Common Issues**

#### **Backend Won't Start**
```bash
# Check Python environment
which python
python --version

# Verify dependencies
pip list | grep fastapi
pip list | grep uvicorn

# Check port availability
lsof -i :8001
```

#### **Frontend Won't Start**
```bash
# Check Node.js version
node --version
npm --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### **API Connection Issues**
```bash
# Check CORS settings in backend/main.py
# Verify frontend API_BASE_URL in src/services/api.js
# Test backend directly: curl http://localhost:8001/health
```

### **VS Code Specific Issues**

#### **Python Interpreter Not Found**
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python`

#### **Terminal Not Activating Virtual Environment**
1. Check `.vscode/settings.json`
2. Ensure `python.terminal.activateEnvironment` is `true`
3. Restart VS Code

---

## **📊 Monitoring & Debugging**

### **Backend Logs**
- **Location**: VS Code Terminal
- **Key Messages**:
  - `INFO: Application startup complete`
  - `INFO: Uvicorn running on http://0.0.0.0:8001`
  - `Models loaded successfully`

### **Frontend Logs**
- **Location**: VS Code Terminal
- **Key Messages**:
  - `webpack compiled successfully`
  - `Local: http://localhost:3002`
  - `On Your Network: http://192.168.x.x:3002`

### **Browser Developer Tools**
- **F12** to open DevTools
- **Console Tab**: JavaScript errors
- **Network Tab**: API requests/responses
- **Application Tab**: Local storage, cookies

---

## **🔧 Environment Variables**

### **Backend Environment**
```bash
# Required
GEMINI_API_KEY=<your_gemini_api_key>

# Optional
PORT=8001
HOST=0.0.0.0
DEBUG=true
```

### **Frontend Environment**
```bash
# Create frontend/.env.local
REACT_APP_API_URL=http://localhost:8001
PORT=3002
```

---

## **📁 Project Structure in VS Code**

### **Explorer View**
```
Lead_Assessment_POC/
├── .vscode/                 # VS Code configuration
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── backend/
│   └── main.py             # Main FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── App.js          # Main React app
│   │   └── App.css         # Global styles
│   └── package.json
├── requirements.txt        # Python dependencies
├── ARCHITECTURE.md         # Architecture documentation
└── RUNTIME_GUIDE.md        # This file
```

---

## **⚡ Quick Start Commands**

### **One-Command Setup**
```bash
# Backend
source venv/bin/activate && GEMINI_API_KEY='<your_gemini_api_key>' python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend
cd frontend && PORT=3002 npm start
```

### **VS Code Shortcuts**
- **Ctrl+Shift+P**: Command Palette
- **Ctrl+`**: Toggle Terminal
- **F5**: Start Debugging
- **Ctrl+F5**: Run Without Debugging
- **Ctrl+Shift+`**: New Terminal

---

## **🎯 Best Practices**

### **Development**
1. **Always activate virtual environment** before running backend
2. **Use VS Code tasks** for consistent startup
3. **Check terminal output** for errors
4. **Test API endpoints** before frontend changes
5. **Use browser DevTools** for debugging

### **File Management**
1. **Keep .vscode/ folder** in version control
2. **Use .gitignore** for node_modules and __pycache__
3. **Document changes** in commit messages
4. **Test both frontend and backend** before committing

---

## **🚀 Production Deployment**

### **Docker Setup**
```bash
# Build and run with Docker
docker-compose up --build
```

### **Environment Configuration**
```bash
# Production environment variables
export GEMINI_API_KEY=your_production_key
export NODE_ENV=production
export REACT_APP_API_URL=https://your-api-domain.com
```

---

This guide provides everything you need to run the Lead Assessment POC application efficiently in VS Code! 🚀
