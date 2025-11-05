# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    GDAL_VERSION=3.8.4

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# Note: GDAL wheel needs to be handled separately or installed via pip
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install GDAL==$(gdal-config --version) && pip install --no-cache-dir -r requirements.txt)

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs /app/results

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create a non-root user
RUN useradd -m -u 1000 farmvision && \
    chown -R farmvision:farmvision /app

# Switch to non-root user
USER farmvision

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Run gunicorn
CMD ["gunicorn", "yolowebapp2.wsgi:application", "--config", "gunicorn_config.py"]
