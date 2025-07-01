# Railway.app Environment Variables for Farm Vision

## Required Environment Variables

### 1. Flask Configuration
```
SESSION_SECRET=your-secret-key-here-32-characters-minimum
FLASK_ENV=production
```

### 2. Database Configuration (Choose one)

#### Option A: SQLite (Simple)
```
DATABASE_URL=sqlite:///farm_vision.db
```

#### Option B: PostgreSQL (Recommended for production)
```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```
*Railway provides PostgreSQL service - add it from their dashboard*

### 3. Application Settings
```
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=104857600
PYTHONPATH=/app
PORT=5000
```

### 4. AI Model Configuration
```
YOLO_MODEL_PATH=detection_models/
TORCH_DEVICE=cpu
CUDA_VISIBLE_DEVICES=-1
```

### 5. File Storage
```
RESULTS_FOLDER=static/results
DETECTED_FOLDER=static/detected
```

## Optional Environment Variables

### For Production Optimization
```
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
WEB_CONCURRENCY=2
```

### For Debug Mode (Development only)
```
FLASK_DEBUG=False
LOG_LEVEL=INFO
```

## Railway.app Setup Steps

1. **Create Railway Project**
   - Go to railway.app
   - Connect GitHub repository
   - Select "Deploy from GitHub"

2. **Add Environment Variables**
   - Go to project → Variables tab
   - Add each variable above
   - Click "Deploy" after adding all

3. **Optional: Add PostgreSQL**
   - Go to project → Add Service
   - Select PostgreSQL
   - Railway will auto-set DATABASE_URL

4. **Deploy Configuration**
   Railway automatically detects Python projects and uses:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT main:app
   ```

## Generate SESSION_SECRET

Use this command to generate a secure secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Important Notes

- Railway assigns a random port ($PORT), don't hardcode port 5000
- Use 0.0.0.0 for host binding, not localhost
- SQLite works but PostgreSQL recommended for production
- All file uploads will be persistent on Railway
- AI models will load automatically on first request

## Sample .env file for local testing
```
SESSION_SECRET=your-generated-secret-key-here
DATABASE_URL=sqlite:///farm_vision.db
UPLOAD_FOLDER=static/uploads
RESULTS_FOLDER=static/results
DETECTED_FOLDER=static/detected
FLASK_ENV=development
```