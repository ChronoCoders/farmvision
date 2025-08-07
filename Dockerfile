# Railway deployment Dockerfile for Farm Vision
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV GDAL_CONFIG=/usr/bin/gdal-config

WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip

# Install PyTorch CPU
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install \
    'email-validator>=1.3.0,<3.0.0' \
    'flask-login>=0.6.0,<1.0.0' \
    'flask>=2.3.0,<4.0.0' \
    'flask-sqlalchemy>=3.0.0,<4.0.0' \
    'gunicorn>=20.1.0,<22.0.0' \
    'psycopg2-binary>=2.9.0,<3.0.0' \
    'scipy>=1.9.0,<2.0.0' \
    'sqlalchemy>=1.4.0,<3.0.0' \
    'werkzeug>=2.3.0,<4.0.0' \
    'pandas>=1.5.0,<2.0.0' \
    'opencv-python-headless>=4.5.0,<5.0.0' \
    'pillow>=9.5.0,<11.0.0' \
    'numpy>=1.24.0,<2.0.0' \
    'matplotlib>=3.7.0' \
    'rasterio>=1.3.0,<2.0.0' \
    'flask-wtf>=1.1.0,<2.0.0' \
    'wtforms>=3.0.0,<4.0.0' \
    'psutil>=5.9.0' \
    'python-dotenv>=1.0.0'

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p static/uploads static/results static/detected static/convertor detection_models logs

# Expose port
EXPOSE 5000

# Start application
CMD ["/opt/venv/bin/gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "main:app"]