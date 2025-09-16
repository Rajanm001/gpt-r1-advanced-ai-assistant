# 🔐 Environment Variables Configuration

This file documents all environment variables used in the ChatGPT Clone application.

## Backend Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dbname` | ✅ |
| `OPENAI_API_KEY` | OpenAI API key for GPT integration | `sk-...` | ✅ |
| `SECRET_KEY` | JWT signing secret | `your-secret-key-here` | ✅ |

### Optional Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `development` | ❌ |
| `DEBUG` | Enable debug mode | `true` | ❌ |
| `API_V1_STR` | API version prefix | `/api/v1` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` | ❌ |
| `ALGORITHM` | JWT algorithm | `HS256` | ❌ |
| `MAX_TOKENS` | OpenAI max tokens | `4000` | ❌ |
| `MODEL_NAME` | OpenAI model | `gpt-3.5-turbo` | ❌ |
| `TEMPERATURE` | OpenAI temperature | `0.7` | ❌ |

### Database Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `POSTGRES_DB` | Database name | `chatgpt_clone` | ✅ |
| `POSTGRES_USER` | Database user | `username` | ✅ |
| `POSTGRES_PASSWORD` | Database password | `password` | ✅ |
| `POSTGRES_HOST` | Database host | `localhost` | ✅ |
| `POSTGRES_PORT` | Database port | `5432` | ✅ |

### CORS Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | Allowed frontend origins | `["http://localhost:3000"]` |

## Frontend Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` | ✅ |

### Optional Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_APP_NAME` | Application name | `ChatGPT Clone` | ❌ |

## Environment Files

### Backend (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/chatgpt_clone
POSTGRES_DB=chatgpt_clone
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Security Configuration
SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=ChatGPT Clone

# Chat Configuration
MAX_TOKENS=4000
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=ChatGPT Clone
```

## Production Configuration

### Backend Production (.env)
```env
# Use secure, production-ready values
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://prod_user:secure_password@prod-db.example.com:5432/chatgpt_clone
OPENAI_API_KEY=sk-your-production-key
SECRET_KEY=very-secure-production-secret-key-with-high-entropy
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### Frontend Production (.env.production)
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=ChatGPT Clone
```

## Docker Environment

### Docker Compose (.env)
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your_secure_secret_key_for_production

# Database (automatically configured in docker-compose.yml)
POSTGRES_DB=chatgpt_clone
POSTGRES_USER=username
POSTGRES_PASSWORD=password
```

## Security Best Practices

### 🔐 Secret Management
- Never commit `.env` files to version control
- Use different secrets for each environment
- Rotate secrets regularly
- Use environment-specific secret management services

### 🛡️ Production Security
- Use strong, randomly generated secret keys
- Enable HTTPS in production
- Restrict CORS origins to your domain
- Use environment variables for all sensitive data
- Enable database SSL connections

### 🔍 Monitoring Variables
```env
# Optional monitoring and logging
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here
REDIS_URL=redis://localhost:6379
```

## Validation

### Environment Validation Script
```bash
#!/bin/bash
# validate-env.sh

echo "Validating environment variables..."

# Check required backend variables
required_vars=("DATABASE_URL" "OPENAI_API_KEY" "SECRET_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

echo "✅ All required environment variables are configured!"
```

## Getting API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### Secret Key Generation
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

## Troubleshooting

### Common Issues

#### Database Connection
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### OpenAI API
```bash
# Test OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### Environment Loading
```python
# Debug environment loading
import os
from dotenv import load_dotenv

load_dotenv()
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("OPENAI_API_KEY:", "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing")
```

---

Keep your environment variables secure and never share them publicly!