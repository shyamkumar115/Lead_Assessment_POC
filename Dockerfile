# Multi-stage build for the Lead Assessment POC application

# Stage 1: Backend
FROM python:3.9-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY data_generator.py .
COPY ml_models.py .

# Create directories for data and models
RUN mkdir -p data models

# Generate sample data and train models
RUN python data_generator.py && python ml_models.py

# Expose backend port
EXPOSE 8000

# Stage 2: Frontend
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 3: Production
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy backend code
COPY --from=backend /app/backend ./backend
COPY --from=backend /app/data_generator.py .
COPY --from=backend /app/ml_models.py .
COPY --from=backend /app/data ./data
COPY --from=backend /app/models ./models

# Copy built frontend from frontend stage
COPY --from=frontend /app/frontend/build ./frontend/build

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose ports
EXPOSE 80 8000

# Start the application
CMD ["./start.sh"]
