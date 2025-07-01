# Railway.app Deployment Guide for Farm Vision

## 🚀 Quick Deployment Steps

### 1. Environment Variables to Add in Railway Dashboard

Copy-paste these into Railway Variables section:

```
SESSION_SECRET=<generate-with-command-below>
DATABASE_URL=sqlite:///farm_vision.db
UPLOAD_FOLDER=static/uploads
RESULTS_FOLDER=static/results
DETECTED_FOLDER=static/detected
MAX_CONTENT_LENGTH=104857600
FLASK_ENV=production
YOLO_MODEL_PATH=detection_models/
TORCH_DEVICE=cpu
PYTHONPATH=/app
```

### 2. Generate SESSION_SECRET
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Railway Auto-Detection
Railway will automatically detect:
- Python project (from pyproject.toml)
- Build command: `pip install -e .`
- Start command: `gunicorn --bind 0.0.0.0:$PORT main:app`

## 📁 Current Project Dependencies (from pyproject.toml)

Railway will install these automatically:
- Flask ecosystem (Flask, SQLAlchemy, Login)
- AI/ML stack (PyTorch, OpenCV, PIL)
- Geospatial (Rasterio, GDAL)
- Web server (Gunicorn)

## 🗄️ Database Options

### Option 1: SQLite (Simple)
```
DATABASE_URL=sqlite:///farm_vision.db
```
✅ No additional setup needed
✅ Works immediately
❌ Single file, no backups

### Option 2: PostgreSQL (Production)
```
1. Add PostgreSQL service in Railway
2. Railway auto-sets DATABASE_URL
3. More robust for production
```

## 🔧 Railway Configuration

Railway reads from your existing files:
- `pyproject.toml` - Dependencies
- `main.py` - Entry point
- `gunicorn` command - Web server

## 📱 Access Your App

After deployment:
- **Auto Domain**: `https://farmvision-production.up.railway.app`
- **IP Access**: Railway provides direct IP access
- **Custom Domain**: Add your own domain in settings

## 🚨 Important Notes

1. **File Storage**: All uploads persist on Railway
2. **Model Loading**: AI models load on first request
3. **Port Binding**: Use `$PORT` environment variable
4. **Memory**: Railway provides sufficient RAM for PyTorch
5. **Build Time**: First deploy takes 5-10 minutes (PyTorch compilation)

## 💡 Deployment Tips

- Keep build logs open to monitor progress
- First AI request may take 30 seconds (model loading)
- Check Railway logs for any startup issues
- All 113 uploaded files included in deployment

## 🔍 Troubleshooting

If deployment fails:
1. Check Railway build logs
2. Ensure all environment variables set
3. Verify GitHub repository connection
4. Contact Railway support for PyTorch issues

Your Farm Vision app will be fully functional with:
✅ Real YOLO v7 AI detection
✅ Turkish agricultural management
✅ Drone mapping capabilities
✅ All 8 fruit detection types
✅ Vegetation analysis algorithms