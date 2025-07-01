FROM python:3.10-slim

# Sistemde ihtiyaç duyulan bağımlılıkları yükle
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

# GDAL ortam değişkeni ayarı
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Çalışma klasörü
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Railway veya benzeri platformlar için port ayarı
ENV PORT=8000

# Başlatma komutu (gerekirse değiştirin)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]
