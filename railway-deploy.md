# Railway.app Deployment Guide for Farm Vision

## Prerequisites
1. Create a Railway account at https://railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Connect your GitHub repository to Railway

## Environment Variables Setup

Add these environment variables in your Railway project dashboard:

### Required Production Environment Variables
```bash
# Application Configuration
SECRET_KEY=your_64_character_secret_key_here
FLASK_ENV=production
DEBUG=false

# Database Configuration (Railway PostgreSQL)
# Railway will automatically provide DATABASE_URL when you add PostgreSQL service

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=52428800
ALLOWED_EXTENSIONS=jpg,jpeg,png,tiff,tif,geotiff

# AI Model Configuration
MODEL_PATH=detection_models
YOLO_CONFIDENCE_THRESHOLD=0.25
YOLO_IOU_THRESHOLD=0.45

# Logging Configuration
LOG_LEVEL=WARNING
LOG_FILE=logs/farm_vision.log

# Security Configuration
WTF_CSRF_ENABLED=true
WTF_CSRF_SECRET_KEY=your_csrf_secret_key_here

# Railway Production Settings
PORT=5000
RAILWAY_ENVIRONMENT=production
```

## Deployment Steps

### Step 1: Create Railway Project
1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Farm Vision repository

### Step 2: Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New Service"
3. Select "PostgreSQL"
4. Railway will automatically set DATABASE_URL environment variable

### Step 3: Configure Environment Variables
1. Go to your app service settings
2. Click "Variables" tab
3. Add all the environment variables listed above
4. Generate SECRET_KEY with: `python -c 'import secrets; print(secrets.token_hex(32))'`

### Step 4: Configure Build Settings
Railway will automatically detect the configuration from:
- `nixpacks.toml` - Build and runtime configuration
- `Procfile` - Start command
- `railway.json` - Railway-specific settings

### Step 5: Deploy
1. Push your code to the connected GitHub repository
2. Railway will automatically trigger a deployment
3. Monitor the build logs in Railway dashboard

## Production Optimizations

### Database Connection
- Railway PostgreSQL is automatically configured with SSL
- Connection pooling is enabled in the app configuration
- Automatic failover and backups included

### Performance Settings
- Gunicorn configured with 2 workers
- Request timeout set to 120 seconds
- Max requests per worker: 1000 with jitter

### Security Features
- HTTPS is automatically enabled by Railway
- Environment variables are securely encrypted
- CSRF protection enabled
- Production-grade secret key required

## Monitoring & Logs
1. View application logs in Railway dashboard
2. Monitor resource usage and metrics
3. Set up health check endpoints
4. Configure alert notifications

## Custom Domain (Optional)
1. In Railway dashboard, go to Settings
2. Click "Domains"
3. Add your custom domain
4. Configure DNS records as instructed

## Troubleshooting

### Common Issues
1. **Build failures**: Check nixpacks.toml configuration
2. **Database connection**: Verify DATABASE_URL is set by PostgreSQL service
3. **Missing directories**: Build phase creates required directories
4. **Environment variables**: Ensure all required variables are set

### Debug Commands
```bash
# View logs
railway logs

# Connect to database
railway connect postgresql

# Run shell in deployment environment
railway shell
```

## Performance Monitoring
- Railway provides built-in metrics
- Application logs are centralized
- Database performance monitoring included
- Automatic scaling based on traffic