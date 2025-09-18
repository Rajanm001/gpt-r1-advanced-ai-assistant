# 🚀 Production Deployment Guide for GPT.R1

## 🌐 Deploy to Render (Recommended)

### Backend Deployment on Render

1. **Create Render Account**: Sign up at [render.com](https://render.com)

2. **Create PostgreSQL Database**:
   ```
   - Service: PostgreSQL
   - Name: gpt-r1-database
   - Plan: Starter (Free) or Starter ($7/month)
   - PostgreSQL Version: 15
   ```

3. **Deploy Backend Service**:
   ```
   - Service: Web Service
   - Repository: Your GitHub repo
   - Name: gpt-r1-backend
   - Root Directory: backend
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables for Backend**:
   ```env
   DATABASE_URL=<your-render-postgres-internal-url>
   OPENAI_API_KEY=sk-your-openai-api-key
   SECRET_KEY=your-super-secure-random-secret-key
   ENVIRONMENT=production
   DEBUG=false
   ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
   ```

### Frontend Deployment on Render

1. **Deploy Frontend Service**:
   ```
   - Service: Static Site
   - Repository: Your GitHub repo
   - Name: gpt-r1-frontend
   - Root Directory: frontend
   - Build Command: npm ci && npm run build
   - Publish Directory: out
   ```

2. **Environment Variables for Frontend**:
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   NEXT_PUBLIC_APP_NAME=GPT.R1 Professional
   ```

---

## ☁️ Deploy to Railway

### One-Click Railway Deployment

1. **Fork Repository**: Fork this repo to your GitHub
2. **Deploy to Railway**: 
   ```
   https://railway.app/new/template/your-repo-url
   ```

3. **Environment Setup**:
   ```env
   # Database (Auto-configured by Railway)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   
   # Required Configuration
   OPENAI_API_KEY=sk-your-openai-api-key
   SECRET_KEY=your-secure-secret-key
   ENVIRONMENT=production
   ```

---

## 🐳 Deploy with Docker on VPS

### Prerequisites
- VPS with Docker and Docker Compose
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/gpt-r1
cd /opt/gpt-r1
```

### Step 2: Clone and Configure
```bash
# Clone repository
git clone https://github.com/Rajanm001/gpt-r1-advanced-ai-assistant.git .

# Create production environment file
cat > .env << EOF
# Database Configuration
POSTGRES_DB=gpt_r1_prod
POSTGRES_USER=gpt_r1_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Security Configuration
SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=GPT.R1 Professional
EOF
```

### Step 3: Deploy with Docker Compose
```bash
# Build and start services
docker-compose -f docker-compose.yml up -d --build

# Check service health
docker-compose ps
docker-compose logs -f

# Verify deployment
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:3000
```

### Step 4: Setup Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/gpt-r1 << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Enable streaming
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/gpt-r1 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test SSL renewal
sudo certbot renew --dry-run
```

---

## 🚀 Deploy to AWS (Advanced)

### Architecture Overview
```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
ECS Fargate Services
├── Frontend (Next.js)
├── Backend (FastAPI)
└── Database (RDS PostgreSQL)
```

### Step 1: Infrastructure Setup
```bash
# Create ECS Cluster
aws ecs create-cluster --cluster-name gpt-r1-cluster

# Create RDS PostgreSQL Instance
aws rds create-db-instance \
  --db-instance-identifier gpt-r1-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your-secure-password \
  --allocated-storage 20
```

### Step 2: Container Deployment
```dockerfile
# Build and push to ECR
aws ecr create-repository --repository-name gpt-r1-backend
aws ecr create-repository --repository-name gpt-r1-frontend

# Tag and push images
docker build -t gpt-r1-backend ./backend
docker tag gpt-r1-backend:latest 123456789.dkr.ecr.region.amazonaws.com/gpt-r1-backend:latest
docker push 123456789.dkr.ecr.region.amazonaws.com/gpt-r1-backend:latest
```

### Step 3: ECS Task Definitions
```json
{
  "family": "gpt-r1-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789.dkr.ecr.region.amazonaws.com/gpt-r1-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "OPENAI_API_KEY", "value": "sk-..."}
      ]
    }
  ]
}
```

---

## 📊 Production Monitoring

### Health Checks Setup
```bash
# Backend health endpoint
curl https://api.yourdomain.com/api/v1/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-09-18T12:00:00Z",
  "database": {"status": "connected"},
  "openai": {"status": "available"}
}
```

### Monitoring Tools
- **Uptime**: UptimeRobot, Pingdom
- **Performance**: New Relic, DataDog
- **Logs**: CloudWatch, Papertrail
- **Errors**: Sentry, Rollbar

### Backup Strategy
```bash
# Automated database backups
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

---

## 🔧 Production Optimizations

### Performance Tuning
1. **Database Connection Pooling**: Configure max connections
2. **Redis Caching**: Cache frequent queries
3. **CDN**: Use CloudFlare for static assets
4. **Compression**: Enable gzip compression
5. **Rate Limiting**: Implement API rate limits

### Security Hardening
1. **HTTPS Only**: Force SSL/TLS
2. **CORS**: Restrict origins to production domains
3. **Headers**: Security headers (HSTS, CSP)
4. **Secrets**: Use environment variables
5. **Updates**: Regular security patches

### Scaling Configuration
```yaml
# Auto-scaling configuration
services:
  backend:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## 🚨 Troubleshooting Production Issues

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL status
pg_isready -h your-db-host -p 5432

# Verify connection string
psql $DATABASE_URL -c "SELECT 1;"
```

#### OpenAI API Errors
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### Frontend Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build

# Check environment variables
env | grep NEXT_PUBLIC
```

### Performance Issues
```bash
# Check container resources
docker stats

# Monitor database queries
# Enable slow query logging in PostgreSQL

# Check API response times
time curl https://api.yourdomain.com/api/v1/health
```

---

## 📋 Production Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Backup strategy implemented
- [ ] Monitoring tools setup

### Security
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Secrets not in code
- [ ] Database secured
- [ ] API rate limiting enabled
- [ ] Security headers configured

### Performance
- [ ] Database optimized
- [ ] Caching implemented
- [ ] CDN configured
- [ ] Load testing completed
- [ ] Auto-scaling configured
- [ ] Logs aggregation setup

### Monitoring
- [ ] Health checks configured
- [ ] Uptime monitoring active
- [ ] Error tracking setup
- [ ] Performance monitoring
- [ ] Backup verification
- [ ] Alert notifications

---

<div align="center">

**🎉 PRODUCTION DEPLOYMENT COMPLETE**

*Your GPT.R1 AI Assistant is now live and ready for users!*

**Monitor**: Health checks and performance  
**Maintain**: Regular updates and backups  
**Scale**: Auto-scaling as usage grows  

</div>