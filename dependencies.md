# Farm Vision - Dependencies

## Projeye Kurulu Kütüphaneler

### Core Flask Framework
- **flask**: 3.1.1+ - Ana web framework
- **flask-login**: 0.6.3+ - Kullanıcı oturumu yönetimi
- **flask-sqlalchemy**: 3.1.1+ - Veritabanı ORM
- **flask-wtf**: 1.2.2+ - Form işleme ve güvenlik
- **wtforms**: 3.2.1+ - Form validation
- **werkzeug**: 3.1.3+ - WSGI utilities

### Database
- **sqlalchemy**: 2.0.41+ - SQL toolkit ve ORM
- **psycopg2-binary**: 2.9.10+ - PostgreSQL adapter
- **email-validator**: 2.2.0+ - Email doğrulama

### AI & Machine Learning
- **torch**: 2.7.1+ - PyTorch deep learning framework
- **torchvision**: 0.22.1+ - Computer vision modelleri
- **opencv-python**: 4.11.0+ - Görüntü işleme

### Scientific Computing
- **numpy**: 2.3.1+ - Sayısal hesaplamalar
- **scipy**: 1.16.0+ - Bilimsel hesaplamalar
- **pandas**: 2.3.0+ - Veri analizi
- **matplotlib**: 3.10.3+ - Grafik çizimi

### Image Processing
- **pillow**: 11.2.1+ - Görüntü işleme kütüphanesi
- **rasterio**: 1.4.3+ - GeoTIFF ve raster dosya işleme

### Web Server
- **gunicorn**: 23.0.0+ - WSGI HTTP Server (Production)

## Kütüphane Yönetimi

### Replit'te Kütüphane Kurma
```bash
# Yeni kütüphane eklemek için
replit package install python:package-name

# Örnek:
replit package install python:requests
```

### pyproject.toml
Tüm kütüphaneler `pyproject.toml` dosyasında tanımlanıyor:
- `[project.dependencies]` bölümünde listeleniyor
- uv package manager ile yönetiliyor
- PyTorch CPU-only versiyonu kullanılıyor (Linux için)

### Production Deployment
Production ortamında aynı kütüphaneler:
- Gunicorn ile serving
- PostgreSQL database
- SSL/TLS support
- Load balancing capability

## Önemli Notlar

1. **PyTorch**: CPU-only version (GPU olmayan ortamlar için optimize)
2. **Database**: Development'ta SQLite, Production'da PostgreSQL
3. **Image Processing**: PIL + OpenCV kombinasyonu
4. **Geospatial**: Rasterio ile GeoTIFF desteği
5. **AI Models**: YOLO v7 ile custom tarımsal modeller

## Version Compatibility

Tüm kütüphaneler Python 3.11+ uyumlu ve stable versiyonlarda tutuluyor.
Major update'ler için önce test environment'ta deneme yapılması öneriliyor.