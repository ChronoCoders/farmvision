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
    gcc=4:10.2.1-1 \
    g++=4:10.2.1-1 \
    postgresql-client=13+225+deb11u1 \
    libpq-dev=13.22-0+deb11u1 \
    libgdal-dev=3.2.2+dfsg-2+deb11u2 \
    gdal-bin=3.2.2+dfsg-2+deb11u2 \
    libproj-dev=7.2.1-1 \
    libgeos-dev=3.9.0-1 \
    libspatialindex-dev=1.9.3-2 \
    git=1:2.30.2-1+deb11u4 \
    wget=1.21-1+deb11u2 \
    curl=7.74.0-1.3+deb11u15 \
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
