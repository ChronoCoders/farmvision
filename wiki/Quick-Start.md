# Quick Start Guide

Get FarmVision up and running in 5 minutes!

## Prerequisites

Before you begin, ensure you have:
- Python 3.10+
- PostgreSQL 13+ running
- Redis 6+ running
- Git installed

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with minimum required settings:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_NAME=farmvision
DATABASE_USER=postgres
DATABASE_PASSWORD=your-postgres-password
DATABASE_HOST=localhost
REDIS_HOST=localhost
```

### 5. Setup Database

```bash
# Create database (if not exists)
createdb farmvision

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

Follow prompts to create your admin account.

### 6. Start Server

```bash
python manage.py runserver
```

### 7. Access Application

Open your browser and navigate to:
- **Application:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin

Login with the superuser credentials you created.

---

## Docker Quick Start

Even faster with Docker!

### 1. Prerequisites

- Docker installed
- Docker Compose installed

### 2. Clone and Start

```bash
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
cp .env.example .env
# Edit .env if needed

# Start all services
docker-compose up -d

# Wait ~30 seconds for services to start, then:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 3. Access

Visit http://localhost:8000

---

## First Steps

### 1. Login

1. Navigate to http://localhost:8000/admin
2. Login with your superuser credentials

### 2. Create Your First Drone Project

1. Click on **Drone Projeleri** in the menu
2. Click the **⋮** (three dots) menu
3. Select **Yeni Proje Ekle** (New Project)
4. Fill in the form:
   - **Çiftlik (Farm):** MyFarm
   - **Tarla (Field):** Field1
   - **Başlık (Title):** Test Project
   - **Durum (Status):** Active
   - **Görsel (Images):** Upload some drone images (JPEG/PNG/TIFF)
5. Click **Kaydet** (Save)

### 3. View Project

Your project appears in the list. Click on the farm name to view the map.

### 4. Try Object Detection

1. Navigate to **Multi Detection** in the menu
2. Upload test images
3. Select a YOLOv8 model (yolov8n for fastest)
4. Click **Process**
5. View detection results with bounding boxes

### 5. Check System Status

Navigate to **System Monitoring** to view:
- CPU and GPU usage
- Memory consumption
- Disk I/O
- Network stats
- Loaded ML models

---

## Common Tasks

### Run Tests

```bash
pytest
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Create Database Backup

```bash
pg_dump farmvision > backup.sql
```

### Start Celery Worker (for async tasks)

```bash
celery -A yolowebapp2 worker -l info
```

---

## API Quick Test

### Get API Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

### List Projects

```bash
curl http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <your-token>"
```

### View API Documentation

- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/schema/redoc/

---

## Troubleshooting

### Server Won't Start

**Check if port 8000 is available:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Solution:** Kill the process or use a different port:
```bash
python manage.py runserver 8001
```

### Database Connection Error

**Verify PostgreSQL is running:**
```bash
pg_isready
```

**Check connection:**
```bash
psql -U postgres -d farmvision -h localhost
```

### Redis Connection Error

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Start Redis if needed:**
```bash
# Linux
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows WSL2
sudo service redis-server start
```

### Module Import Errors

**Reinstall dependencies:**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

Now that you're up and running:

1. **[User Guide](User-Guide)** - Learn how to use all features
2. **[Configuration](Configuration)** - Customize your installation
3. **[API Documentation](API-Documentation)** - Integrate with other systems
4. **[Development Setup](Development-Setup)** - Set up for development
5. **[Production Deployment](Production-Deployment)** - Deploy to production

---

## Need Help?

- **Documentation:** [Wiki Home](Home)
- **Issues:** [GitHub Issues](https://github.com/ChronoCoders/farmvision/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ChronoCoders/farmvision/discussions)
- **Email:** support@farmvision.com

---

**Congratulations! 🎉**

You now have FarmVision running. Start exploring the features!
