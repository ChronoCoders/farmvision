# Railway deployment Dockerfile for Farm Vision
FROM python:3.11-slim

# Install system dependencies in single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    gdal-bin libgdal-dev libproj-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GDAL_CONFIG=/usr/bin/gdal-config \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt* pyproject.toml* ./

# Create venv and install dependencies in single layer
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    /opt/venv/bin/pip install --no-cache-dir \
        'flask>=2.3.0,<4.0.0' \
        'flask-sqlalchemy>=3.0.0,<4.0.0' \
        'flask-login>=0.6.0,<1.0.0' \
        'flask-wtf>=1.1.0,<2.0.0' \
        'gunicorn>=20.1.0,<22.0.0' \
        'psycopg2-binary>=2.9.0,<3.0.0' \
        'sqlalchemy>=1.4.0,<3.0.0' \
        'werkzeug>=2.3.0,<4.0.0' \
        'wtforms>=3.0.0,<4.0.0' \
        'email-validator>=1.3.0,<3.0.0' \
        'python-dotenv>=1.0.0' \
        'numpy>=1.24.0,<2.0.0' \
        'pandas>=1.5.0,<2.0.0' \
        'pillow>=9.5.0,<11.0.0' \
        'opencv-python-headless>=4.5.0,<5.0.0' \
        'matplotlib>=3.7.0' \
        'scipy>=1.9.0,<2.0.0' \
        'rasterio>=1.3.0,<2.0.0' \
        'psutil>=5.9.0' && \
    rm -rf /root/.cache/pip

# Copy application code
COPY . .

# Create directories and set permissions in single layer
RUN mkdir -p static/uploads static/results static/detected static/convertor detection_models logs && \
    chmod -R 755 static/ detection_models/ logs/

# Start application
CMD ["/bin/bash", "-c", "/opt/venv/bin/gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 main:app"]