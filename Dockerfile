FROM python:3.10-slim

# Sistem bağımlılıkları
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
    curl \
    && apt-get clean

# GDAL ortam değişkenleri
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Çalışma dizini
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port ayarı
ENV PORT=8000

# Başlatma komutu (Django için uyarlayabilirsiniz)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]
