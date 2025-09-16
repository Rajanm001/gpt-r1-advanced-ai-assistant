# 🚀 Deployment Guide

This guide covers various deployment strategies for the ChatGPT Clone application.

## 📋 Pre-deployment Checklist

- [ ] OpenAI API key configured
- [ ] Database connection tested
- [ ] Environment variables set
- [ ] Application tested locally
- [ ] Security configurations reviewed
- [ ] Performance optimization completed

## 🐳 Docker Deployment (Recommended)

### Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd chatgpt-clone

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Production Docker Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

## ☁️ Cloud Deployment Options

### 1. Vercel + Railway (Recommended for MVP)

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

#### Backend + Database (Railway)
1. Connect GitHub repository to Railway
2. Deploy PostgreSQL add-on
3. Deploy FastAPI application
4. Set environment variables

### 2. AWS Deployment

#### Using AWS ECS + RDS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push images
docker tag chatgpt-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/chatgpt-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/chatgpt-backend:latest
```

### 3. Google Cloud Platform

#### Using Cloud Run + Cloud SQL
```bash
# Deploy to Cloud Run
gcloud run deploy chatgpt-backend \
  --image gcr.io/PROJECT-ID/chatgpt-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 4. DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy application

## 🔧 Environment Configuration

### Production Environment Variables

#### Backend (.env)
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/chatgpt_clone
OPENAI_API_KEY=your_production_openai_key
SECRET_KEY=your_secure_production_secret_key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

#### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_APP_NAME=ChatGPT Clone
```

## 🛡️ Security Considerations

### SSL/TLS Configuration
```nginx
# Nginx configuration for HTTPS
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Rate Limiting
```python
# FastAPI rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request):
    # Chat logic
    pass
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# Add to FastAPI app
import logging
from prometheus_fastapi_instrumentator import Instrumentator

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🚀 Performance Optimization

### Database Optimization
```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### Caching Strategy
```python
# Redis caching
import redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="chatgpt-cache")
```

### CDN Configuration
```javascript
// Next.js optimization
module.exports = {
  images: {
    domains: ['your-cdn-domain.com'],
  },
  experimental: {
    optimizeCss: true,
  },
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy commands here
```

## 🗄️ Database Migration

### Production Migration Strategy
```bash
# Backup database
pg_dump $DATABASE_URL > backup.sql

# Run migrations
cd backend
source venv/bin/activate
alembic upgrade head

# Verify migration
alembic current
```

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatgpt-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatgpt-backend
  template:
    metadata:
      labels:
        app: chatgpt-backend
    spec:
      containers:
      - name: backend
        image: chatgpt-backend:latest
        ports:
        - containerPort: 8000
```

### Load Balancing
```nginx
# Nginx load balancer
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database connectivity
pg_isready -h hostname -p port -U username

# Verify environment variables
echo $DATABASE_URL
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats

# Increase container memory
docker run -m 2g chatgpt-backend
```

#### SSL Certificate Issues
```bash
# Verify certificate
openssl x509 -in certificate.crt -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443
```

## 📞 Support & Maintenance

### Backup Strategy
```bash
# Automated database backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > "backup_$DATE.sql"
aws s3 cp "backup_$DATE.sql" s3://your-backup-bucket/
```

### Update Procedure
```bash
# Zero-downtime update
1. Deploy new version to staging
2. Run database migrations
3. Update backend instances one by one
4. Update frontend with new API version
5. Monitor for issues
```

## 📋 Post-Deployment Checklist

- [ ] Application is accessible via HTTPS
- [ ] Database connections are working
- [ ] Authentication flow is functional
- [ ] Chat streaming is working correctly
- [ ] RAG search is operational
- [ ] Error monitoring is active
- [ ] Backup procedures are in place
- [ ] Performance metrics are being collected

## 🚨 Emergency Procedures

### Rollback Strategy
```bash
# Quick rollback
docker-compose down
docker-compose up -d --scale backend=0
# Deploy previous version
docker-compose up -d
```

### Contact Information
- **Technical Lead**: your-email@example.com
- **Operations**: ops@example.com
- **Emergency**: +1-xxx-xxx-xxxx

---

This deployment guide ensures a smooth transition from development to production while maintaining security, performance, and reliability standards.