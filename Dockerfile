FROM python:3.10-slim

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-gdal \
    gdal-bin \
    libgdal-dev \
    libgl1 \
    libglib2.0-0 \
    git \
    curl

# GDAL ortam değişkenleri
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Çalışma dizini
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --root-user-action=ignore --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.cache /root/.npm /tmp/*

# Proje dosyalarını kopyala
COPY . .

# Port ayarı
ENV PORT=8000

# Başlatma komutu (gerekirse değiştirin: Django -> wsgi:application vs.)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]
