# Lead Assessment POC - Deployment Guide

This guide covers different deployment options for the Lead Assessment POC application.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Option 1: Automated Setup
```bash
# Clone the repository
git clone <repository-url>
cd Lead_Assessment_POC

# Run the automated setup script
python run_local.py
```

### Option 2: Manual Setup
```bash
# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python data_generator.py
python ml_models.py

# Frontend setup
cd frontend
npm install
npm start

# Backend (in another terminal)
cd ..
source venv/bin/activate
uvicorn backend.main:app --reload
```

## 🐳 Docker Deployment

### Single Container
```bash
# Build and run
docker build -t lead-assessment-poc .
docker run -p 80:80 -p 8000:8000 lead-assessment-poc
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS App Runner
1. Push code to GitHub
2. Create App Runner service
3. Connect to GitHub repository
4. Configure build settings:
   - Build command: `docker build -t lead-assessment-poc .`
   - Start command: `./start.sh`
   - Port: 80

#### Using AWS ECS with Fargate
1. Build and push Docker image to ECR
2. Create ECS cluster
3. Create task definition
4. Create service
5. Configure load balancer

### Google Cloud Platform

#### Using Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/lead-assessment-poc
gcloud run deploy --image gcr.io/PROJECT_ID/lead-assessment-poc --platform managed
```

### Azure

#### Using Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image lead-assessment-poc .

# Deploy to Container Instances
az container create --resource-group myResourceGroup --name lead-assessment-poc --image myregistry.azurecr.io/lead-assessment-poc:latest --ports 80 8000
```

## 🔧 Environment Configuration

### Environment Variables
Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Key variables to configure:
- `OPENAI_API_KEY`: For LLM features
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key
- `REACT_APP_API_URL`: Frontend API URL

### Production Considerations

#### Security
- Use HTTPS in production
- Set strong secret keys
- Configure CORS properly
- Enable rate limiting
- Use environment variables for secrets

#### Performance
- Enable gzip compression
- Configure caching headers
- Use CDN for static assets
- Set up database connection pooling
- Monitor resource usage

#### Monitoring
- Set up health checks
- Configure logging
- Monitor API performance
- Set up alerts for errors

## 📊 Data Portal Integration

### Embedding in Data Portal
The application can be embedded in existing data portals:

1. **Iframe Integration**:
```html
<iframe 
  src="https://your-domain.com" 
  width="100%" 
  height="800px"
  frameborder="0">
</iframe>
```

2. **API Integration**:
```javascript
// Use the API endpoints directly
const response = await fetch('https://your-api-domain.com/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ leads: leadData })
});
```

3. **Widget Integration**:
```javascript
// Load as a widget
const script = document.createElement('script');
script.src = 'https://your-domain.com/widget.js';
document.head.appendChild(script);
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy Lead Assessment POC

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker build -t lead-assessment-poc .
          docker run -d -p 80:80 lead-assessment-poc
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**:
   - Change ports in docker-compose.yml
   - Update nginx.conf for different ports

2. **Memory issues**:
   - Increase Docker memory limits
   - Optimize model loading

3. **API connection issues**:
   - Check CORS configuration
   - Verify API URL in frontend

4. **Model loading errors**:
   - Ensure models are trained
   - Check file permissions

### Logs
```bash
# Docker logs
docker logs <container-id>

# Application logs
tail -f logs/app.log

# Nginx logs
docker exec <container-id> tail -f /var/log/nginx/error.log
```

## 📈 Scaling

### Horizontal Scaling
- Use load balancer
- Deploy multiple backend instances
- Use shared database
- Implement session management

### Vertical Scaling
- Increase container resources
- Optimize model inference
- Use GPU acceleration
- Implement caching

## 🔐 Security Checklist

- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Regular security updates
- [ ] Monitoring and alerting

## 📞 Support

For deployment issues:
1. Check the logs
2. Verify environment configuration
3. Test API endpoints
4. Check network connectivity
5. Review security settings
