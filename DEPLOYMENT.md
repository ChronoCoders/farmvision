# Farm Vision - Railway.app Deployment

Farm Vision is now ready for production deployment on Railway.app! Here's everything you need to deploy successfully.

## Quick Start (5 Minutes)

### 1. Create Railway Account
- Visit https://railway.app and create an account
- Connect your GitHub account

### 2. Deploy from GitHub
1. Click "New Project" in Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your Farm Vision repository
4. Railway will automatically start building

### 3. Add PostgreSQL Database
1. In your project dashboard, click "New Service"
2. Select "PostgreSQL"
3. Railway automatically sets up `DATABASE_URL`

### 4. Configure Environment Variables
Add these in Railway dashboard (Variables section):

```bash
SECRET_KEY=your_64_character_secret_key_generate_this
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
WTF_CSRF_ENABLED=true
WTF_CSRF_SECRET_KEY=your_csrf_secret_key_here
```

### 5. Generate Secret Keys
Run this command to generate secure keys:
```bash
python -c 'import secrets; print("SECRET_KEY=" + secrets.token_hex(32)); print("WTF_CSRF_SECRET_KEY=" + secrets.token_hex(32))'
```

## Production Features

### ✅ Production-Ready Configuration
- **Enterprise Security**: CSRF protection, secure session management, production-grade secret keys
- **Database Optimization**: PostgreSQL with connection pooling, SSL enforcement, automatic failover
- **Performance Tuning**: Gunicorn with optimized worker configuration, request timeouts, connection limits
- **Error Handling**: Comprehensive logging, graceful degradation, user-friendly error messages
- **Mobile Responsive**: Enhanced CSS with breakpoints, touch-friendly interface
- **Map Functionality**: Robust tile layer fallbacks, offline error handling, loading indicators

### 🚀 Railway.app Optimizations
- **Automatic HTTPS**: SSL certificates and HTTPS redirection
- **Horizontal Scaling**: Multi-worker Gunicorn configuration
- **Health Monitoring**: Built-in health checks and crash recovery
- **Zero-Downtime Deployments**: Rolling updates with traffic switching
- **Database Backups**: Automatic PostgreSQL backups and point-in-time recovery

## Configuration Files

All deployment files are included:
- `nixpacks.toml` - Build configuration with GDAL/PROJ support
- `Procfile` - Production start command
- `railway.json` - Railway-specific settings
- Production-optimized Flask configuration

## Environment Variables Reference

```bash
# Core Application (Required)
SECRET_KEY=your_64_character_secret_key
FLASK_ENV=production
DEBUG=false

# Security (Required) 
WTF_CSRF_ENABLED=true
WTF_CSRF_SECRET_KEY=your_csrf_secret_key

# Database (Auto-configured by Railway PostgreSQL)
DATABASE_URL=postgresql://... (automatically set)

# File Uploads (Optional - defaults provided)
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=52428800
ALLOWED_EXTENSIONS=jpg,jpeg,png,tiff,tif,geotiff

# AI Models (Optional - defaults provided)
MODEL_PATH=detection_models
YOLO_CONFIDENCE_THRESHOLD=0.25
YOLO_IOU_THRESHOLD=0.45

# Logging (Optional - defaults provided)
LOG_LEVEL=WARNING
LOG_FILE=logs/farm_vision.log
```

## Post-Deployment Checklist

### 1. Test Core Features
- [ ] User registration and login
- [ ] Image upload and AI detection
- [ ] Map visualization with GeoTIFF files
- [ ] Vegetation analysis calculations
- [ ] Dashboard statistics and reporting

### 2. Verify Security
- [ ] HTTPS is enabled (automatic on Railway)
- [ ] CSRF tokens are working
- [ ] Database connections use SSL
- [ ] File upload validation works
- [ ] Error pages don't expose sensitive info

### 3. Performance Check
- [ ] Page load times under 3 seconds
- [ ] Image processing completes successfully
- [ ] Map tiles load properly
- [ ] Mobile interface works smoothly
- [ ] Database queries perform well

## Custom Domain (Optional)

To use your own domain:
1. Go to Railway project Settings
2. Click "Domains" 
3. Add your domain
4. Update your DNS with provided CNAME records

## Monitoring & Maintenance

### Built-in Monitoring
- Application logs in Railway dashboard
- Database performance metrics
- Resource usage (CPU, memory, storage)
- Request volume and response times

### Health Checks
Railway automatically monitors:
- Application availability (HTTP 200 responses)
- Database connectivity
- Resource limits and scaling triggers

## Troubleshooting

### Common Issues
**Build Fails**: Check nixpacks.toml for missing system dependencies
**Database Connection**: Verify PostgreSQL service is running and DATABASE_URL is set
**File Uploads**: Ensure upload directories exist (created automatically in build)
**Map Loading**: Check tile server connectivity and error handling

### Debug Commands
```bash
# View logs
railway logs --follow

# Connect to database
railway connect postgresql

# Access shell
railway shell
```

## Cost Optimization

Railway.app pricing is usage-based:
- **Development**: Free tier available
- **Production**: Pay per resource usage
- **Database**: PostgreSQL costs scale with storage/compute
- **Bandwidth**: Generous free tier, then per-GB

## Support & Updates

Farm Vision includes:
- Production-grade error handling
- Comprehensive logging for debugging  
- Mobile-optimized interface
- Enterprise security features
- Database migration support

Deploy confidently knowing your agricultural AI platform is production-ready! 🌱