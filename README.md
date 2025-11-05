# FarmVision - AI-Powered Agricultural Analysis Platform

FarmVision is an advanced agricultural intelligence platform that combines drone imagery processing with YOLOv8-based object detection to provide comprehensive farm management and analysis capabilities.

## Features

- **Drone Project Management**: Create, manage, and organize drone survey projects
- **AI-Powered Detection**: YOLOv8-based multi-object detection for agricultural analysis
- **Orthophoto Processing**: Automated processing of drone imagery into georeferenced orthophotos
- **Interactive Mapping**: WebODM integration for detailed field visualization
- **Real-time Monitoring**: System monitoring dashboard with CPU, GPU, and memory metrics
- **Multi-Model Support**: Support for various detection models and configurations
- **RESTful API**: Comprehensive API for integration with other systems
- **Turkish Language Support**: Full Turkish language interface

## Tech Stack

- **Backend**: Django 4.2.17
- **AI/ML**: YOLOv8 (Ultralytics), PyTorch, OpenCV
- **GIS**: GDAL, Rasterio, PyProj
- **Database**: PostgreSQL (with PostGIS support)
- **Cache**: Redis
- **Task Queue**: Celery
- **API**: Django REST Framework
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Server**: Gunicorn

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- GDAL 3.8+
- CUDA-capable GPU (recommended for AI processing)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ChronoCoders/farmvision.git
cd farmvision
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
DJANGO_ENVIRONMENT=production
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_NAME=farmvision
DATABASE_USER=farmvision_user
DATABASE_PASSWORD=your-database-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static
```

### 5. Database Setup

```bash
# Create database
createdb farmvision

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Docker Installation

### Using Docker Compose

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f
```

## Usage

### Creating a Drone Project

1. Navigate to **Drone Projeleri** in the menu
2. Click the three-dot menu and select **Yeni Proje Ekle**
3. Fill in project details:
   - Farm Name (Çiftlik)
   - Field Name (Tarla)
   - Project Title (Başlık)
   - Status (Durum)
   - Upload drone images
4. Click **Kaydet** to save

### Running Object Detection

1. Navigate to **Multi Detection**
2. Upload images for analysis
3. Select detection model
4. Click **Process** to run detection
5. View results with bounding boxes and classifications

### System Monitoring

1. Navigate to **System Monitoring**
2. View real-time metrics:
   - CPU usage and core count
   - GPU utilization
   - Memory usage
   - Disk I/O
   - Network statistics
   - Loaded ML models

## API Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

### Authentication

```bash
# Obtain token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in requests
curl http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <your-token>"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest detection/tests/test_views.py
```

### Code Quality

```bash
# Linting with flake8
flake8 .

# Type checking with mypy
mypy .

# Code formatting with black
black .

# Security check with bandit
bandit -r .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Project Structure

```
farmvision/
├── detection/              # Detection app (YOLOv8 integration)
├── dron_map/              # Drone project management
├── yolowebapp2/           # Main Django project
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── WebODM/               # WebODM integration (submodule)
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── gunicorn_config.py    # Gunicorn configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # This file
```

## Configuration

### Settings

Key settings can be configured via environment variables or `yolowebapp2/settings.py`:

- `DEBUG`: Enable/disable debug mode
- `ALLOWED_HOSTS`: Allowed host/domain names
- `DATABASES`: Database configuration
- `CACHES`: Redis cache configuration
- `CELERY_*`: Celery task queue settings

### Models

Place YOLOv8 models in the `weights/` directory:
- `yolov8n.pt` - Nano model (fastest)
- `yolov8s.pt` - Small model
- `yolov8m.pt` - Medium model
- `yolov8l.pt` - Large model
- `yolov8x.pt` - Extra large model (most accurate)

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Use PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Configure logging and monitoring
- [ ] Set up Celery workers
- [ ] Use Gunicorn with nginx reverse proxy

### Gunicorn

```bash
gunicorn yolowebapp2.wsgi:application \
  --config gunicorn_config.py
```

### Celery Workers

```bash
# Start Celery worker
celery -A yolowebapp2 worker -l info

# Start Celery beat (for scheduled tasks)
celery -A yolowebapp2 beat -l info
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U farmvision_user -d farmvision -h localhost
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### GDAL Installation Issues

Windows users: Download the appropriate GDAL wheel from the project or use OSGeo4W.

Linux users:
```bash
sudo apt-get install gdal-bin libgdal-dev
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- FarmVision Team

## Acknowledgments

- YOLOv8 by Ultralytics
- WebODM for drone image processing
- Django community
- All contributors

## Support

For support, please open an issue on GitHub or contact support@farmvision.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
