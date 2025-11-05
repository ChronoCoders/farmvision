# Installation Guide

Complete installation guide for FarmVision on various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Windows Installation](#windows-installation)
- [Linux Installation](#linux-installation)
- [macOS Installation](#macos-installation)
- [Docker Installation](#docker-installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Recommended | Purpose |
|----------|----------------|-------------|---------|
| Python | 3.10 | 3.10+ | Runtime environment |
| PostgreSQL | 13 | 15+ | Database |
| Redis | 6 | 7+ | Caching & task queue |
| GDAL | 3.6 | 3.8.4 | GIS processing |

### Optional Software

- **Docker** (19.03+) - For containerized deployment
- **Nginx** (1.18+) - For production reverse proxy
- **CUDA** (11.8+) - For GPU acceleration (YOLOv8)

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB
- GPU: Not required (CPU inference supported)

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 200+ GB SSD
- GPU: NVIDIA GPU with 8GB+ VRAM (for faster AI processing)

---

## Windows Installation

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### Step 2: Install PostgreSQL

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer (include pgAdmin and command line tools)
3. Set password for `postgres` user
4. Create database:
   ```cmd
   psql -U postgres
   CREATE DATABASE farmvision;
   CREATE USER farmvision_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE farmvision TO farmvision_user;
   \q
   ```

### Step 3: Install PostGIS

1. Launch Stack Builder (included with PostgreSQL)
2. Select your PostgreSQL installation
3. Navigate to Spatial Extensions
4. Install PostGIS
5. Enable PostGIS on database:
   ```sql
   psql -U postgres -d farmvision
   CREATE EXTENSION postgis;
   \q
   ```

### Step 4: Install Redis

**Option A: Using WSL2 (Recommended)**
```bash
wsl --install
# After WSL2 is installed:
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option B: Windows Native**
Download Redis for Windows from [github.com/microsoftarchive/redis](https://github.com/microsoftarchive/redis/releases)

### Step 5: Install GDAL

Download GDAL wheel from the project:
```cmd
cd C:\farmvision
pip install GDAL-3.8.4-cp310-cp310-win_amd64.whl
```

Or use OSGeo4W:
1. Download OSGeo4W from [trac.osgeo.org](https://trac.osgeo.org/osgeo4w/)
2. Install GDAL package
3. Set environment variables

### Step 6: Clone Repository

```cmd
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
```

### Step 7: Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 8: Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 9: Configure Environment

```cmd
copy .env.example .env
notepad .env
```

Edit `.env` with your settings:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_NAME=farmvision
DATABASE_USER=farmvision_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Step 10: Run Migrations

```cmd
python manage.py migrate
```

### Step 11: Create Superuser

```cmd
python manage.py createsuperuser
```

### Step 12: Collect Static Files

```cmd
python manage.py collectstatic --noinput
```

### Step 13: Run Development Server

```cmd
python manage.py runserver
```

Visit: http://localhost:8000

---

## Linux Installation

### Ubuntu/Debian

#### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

#### Step 2: Install System Dependencies

```bash
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql-15 \
    postgresql-15-postgis-3 \
    redis-server \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    git \
    build-essential
```

#### Step 3: Configure PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE farmvision;
CREATE USER farmvision_user WITH PASSWORD 'your_password';
ALTER ROLE farmvision_user SET client_encoding TO 'utf8';
ALTER ROLE farmvision_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE farmvision_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE farmvision TO farmvision_user;
\c farmvision
CREATE EXTENSION postgis;
\q
```

#### Step 4: Start Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Step 5: Clone and Setup

```bash
cd /opt
sudo git clone https://github.com/ChronoCoders/farmvision.git
sudo chown -R $USER:$USER farmvision
cd farmvision
```

#### Step 6: Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 7: Configure Environment

```bash
cp .env.example .env
nano .env
```

#### Step 8: Setup Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### Step 9: Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### CentOS/RHEL

```bash
# Enable EPEL
sudo dnf install epel-release -y

# Install dependencies
sudo dnf install -y python310 postgresql15-server postgresql15-contrib \
    redis gdal gdal-devel git

# Initialize PostgreSQL
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Follow similar steps as Ubuntu above
```

---

## macOS Installation

### Step 1: Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Dependencies

```bash
brew install python@3.10 postgresql@15 redis gdal git
```

### Step 3: Start Services

```bash
brew services start postgresql@15
brew services start redis
```

### Step 4: Create Database

```bash
createdb farmvision
psql farmvision
CREATE USER farmvision_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE farmvision TO farmvision_user;
CREATE EXTENSION postgis;
\q
```

### Step 5: Clone and Setup

```bash
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure and Run

```bash
cp .env.example .env
# Edit .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Docker Installation

### Step 1: Install Docker

**Windows:** [Docker Desktop](https://www.docker.com/products/docker-desktop)
**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
**macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 2: Install Docker Compose

Usually included with Docker Desktop. For Linux:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Clone Repository

```bash
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
```

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 5: Build and Start

```bash
docker-compose up -d
```

### Step 6: Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### Step 7: Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 8: Access Application

Visit: http://localhost:8000

---

## Post-Installation

### 1. Verify Installation

```bash
python manage.py check
```

### 2. Run Tests

```bash
pytest
```

### 3. Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/sample_data.json
```

### 4. Download YOLOv8 Models (Optional)

Models will be downloaded automatically on first use, or manually:

```bash
mkdir -p weights
cd weights
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### 5. Setup Celery Workers (Production)

```bash
# Terminal 1: Start Celery worker
celery -A yolowebapp2 worker -l info

# Terminal 2: Start Celery beat
celery -A yolowebapp2 beat -l info
```

---

## Troubleshooting

### Database Connection Error

**Problem:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
# Windows: Check Services app

# Check connection
psql -U postgres -h localhost

# Verify .env settings
cat .env | grep DATABASE
```

### Redis Connection Error

**Problem:** `redis.exceptions.ConnectionError`

**Solutions:**
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Start Redis
sudo systemctl start redis-server  # Linux
sudo service redis-server start    # WSL2
```

### GDAL Import Error

**Problem:** `ImportError: cannot import name 'gdal' from 'osgeo'`

**Solutions:**
```bash
# Verify GDAL installation
gdalinfo --version

# Reinstall GDAL
pip uninstall GDAL
pip install GDAL==$(gdal-config --version)
```

### Port Already in Use

**Problem:** `Error: That port is already in use`

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python manage.py runserver 8001
```

### Permission Denied

**Problem:** Permission errors when creating directories

**Solutions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/farmvision

# Fix permissions
chmod -R 755 media static
```

---

## Next Steps

- [Quick Start Guide](Quick-Start)
- [Configuration Guide](Configuration)
- [User Guide](User-Guide)
- [API Documentation](API-Documentation)

---

**Need Help?**
- [GitHub Issues](https://github.com/ChronoCoders/farmvision/issues)
- [GitHub Discussions](https://github.com/ChronoCoders/farmvision/discussions)
- Email: support@farmvision.com
