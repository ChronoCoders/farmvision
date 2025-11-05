# FarmVision - Yapay Zeka Destekli Tarımsal Analiz Platformu

[English](README.md) | **Türkçe**

FarmVision, drone görüntü işleme ve YOLOv8 tabanlı nesne tespiti teknolojilerini birleştirerek kapsamlı çiftlik yönetimi ve analiz yetenekleri sunan gelişmiş bir tarımsal zeka platformudur.

## Özellikler

- **Drone Proje Yönetimi**: Drone survey projelerini oluşturma, yönetme ve düzenleme
- **Yapay Zeka Destekli Tespit**: Tarımsal analiz için YOLOv8 tabanlı çoklu nesne tespiti
- **Ortofoto İşleme**: Drone görüntülerinin otomatik olarak coğrafi referanslı ortofotolara dönüştürülmesi
- **İnteraktif Haritalama**: Detaylı tarla görselleştirmesi için WebODM entegrasyonu
- **Gerçek Zamanlı İzleme**: CPU, GPU ve bellek metrikleri içeren sistem izleme kontrol paneli
- **Çoklu Model Desteği**: Çeşitli tespit modelleri ve konfigürasyonları için destek
- **RESTful API**: Diğer sistemlerle entegrasyon için kapsamlı API
- **Türkçe Dil Desteği**: Tam Türkçe dil arayüzü

## Teknoloji Yığını

- **Backend**: Django 4.2.17
- **Yapay Zeka/ML**: YOLOv8 (Ultralytics), PyTorch, OpenCV
- **CBS**: GDAL, Rasterio, PyProj
- **Veritabanı**: PostgreSQL (PostGIS desteği ile)
- **Önbellek**: Redis
- **Görev Kuyruğu**: Celery
- **API**: Django REST Framework
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Sunucu**: Gunicorn

## Gereksinimler

- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- GDAL 3.8+
- CUDA destekli GPU (yapay zeka işleme için önerilir)

## Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/kullaniciadi/farmvision.git
cd farmvision
```

### 2. Sanal Ortam Oluşturun

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam Yapılandırması

Proje kök dizininde bir `.env` dosyası oluşturun:

```env
# Django Ayarları
DJANGO_ENVIRONMENT=production
DJANGO_SECRET_KEY=buraya-gizli-anahtarinizi-girin
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,domainadi.com

# Veritabanı
DATABASE_NAME=farmvision
DATABASE_USER=farmvision_user
DATABASE_PASSWORD=veritabani-sifreniz
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Uygulama
MEDIA_ROOT=/medya/dosya/yolu
STATIC_ROOT=/statik/dosya/yolu
```

### 5. Veritabanı Kurulumu

```bash
# Veritabanı oluştur
createdb farmvision

# Migration'ları çalıştır
python manage.py migrate

# Süper kullanıcı oluştur
python manage.py createsuperuser

# Statik dosyaları topla
python manage.py collectstatic --noinput
```

### 6. Geliştirme Sunucusunu Çalıştırın

```bash
python manage.py runserver
```

Tarayıcınızda `http://localhost:8000` adresini ziyaret edin.

## Docker Kurulumu

### Docker Compose Kullanımı

```bash
# Servisleri oluştur ve başlat
docker-compose up -d

# Migration'ları çalıştır
docker-compose exec web python manage.py migrate

# Süper kullanıcı oluştur
docker-compose exec web python manage.py createsuperuser

# Logları görüntüle
docker-compose logs -f
```

## Kullanım

### Drone Projesi Oluşturma

1. Menüden **Drone Projeleri** bölümüne gidin
2. Üç nokta menüsüne tıklayın ve **Yeni Proje Ekle**'yi seçin
3. Proje detaylarını doldurun:
   - Çiftlik Adı
   - Tarla Adı
   - Proje Başlığı
   - Durum
   - Drone görüntülerini yükleyin
4. Kaydetmek için **Kaydet** butonuna tıklayın

### Nesne Tespiti Çalıştırma

1. **Multi Detection** bölümüne gidin
2. Analiz için görüntüleri yükleyin
3. Tespit modelini seçin
4. Tespiti çalıştırmak için **Process** butonuna tıklayın
5. Sınırlayıcı kutular ve sınıflandırmalarla sonuçları görüntüleyin

### Sistem İzleme

1. **System Monitoring** bölümüne gidin
2. Gerçek zamanlı metrikleri görüntüleyin:
   - CPU kullanımı ve çekirdek sayısı
   - GPU kullanımı
   - Bellek kullanımı
   - Disk I/O
   - Ağ istatistikleri
   - Yüklenmiş ML modelleri

## API Dokümantasyonu

API dokümantasyonu şu adreslerde mevcuttur:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

### Kimlik Doğrulama

```bash
# Token al
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kullanici", "password": "sifre"}'

# İsteklerde token kullan
curl http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <token>"
```

## Geliştirme

### Testleri Çalıştırma

```bash
# Tüm testler
pytest

# Coverage ile
pytest --cov=. --cov-report=html

# Belirli test dosyası
pytest detection/tests/test_views.py
```

### Kod Kalitesi

```bash
# flake8 ile linting
flake8 .

# mypy ile tip kontrolü
mypy .

# black ile kod formatlama
black .

# bandit ile güvenlik kontrolü
bandit -r .
```

### Pre-commit Hook'ları

```bash
# Pre-commit hook'larını yükle
pre-commit install

# Manuel çalıştır
pre-commit run --all-files
```

## Proje Yapısı

```
farmvision/
├── detection/              # Detection uygulaması (YOLOv8 entegrasyonu)
├── dron_map/              # Drone proje yönetimi
├── yolowebapp2/           # Ana Django projesi
├── templates/             # HTML şablonları
├── static/                # Statik dosyalar (CSS, JS, görseller)
├── media/                 # Kullanıcı yüklenen dosyalar
├── WebODM/               # WebODM entegrasyonu (submodule)
├── requirements.txt       # Python bağımlılıkları
├── manage.py             # Django yönetim scripti
├── gunicorn_config.py    # Gunicorn yapılandırması
├── Dockerfile            # Docker yapılandırması
├── docker-compose.yml    # Docker Compose yapılandırması
└── README.md            # Bu dosya
```

## Yapılandırma

### Ayarlar

Temel ayarlar ortam değişkenleri veya `yolowebapp2/settings.py` üzerinden yapılandırılabilir:

- `DEBUG`: Debug modunu etkinleştir/devre dışı bırak
- `ALLOWED_HOSTS`: İzin verilen host/domain isimleri
- `DATABASES`: Veritabanı yapılandırması
- `CACHES`: Redis önbellek yapılandırması
- `CELERY_*`: Celery görev kuyruğu ayarları

### Modeller

YOLOv8 modellerini `weights/` dizinine yerleştirin:
- `yolov8n.pt` - Nano model (en hızlı)
- `yolov8s.pt` - Small model
- `yolov8m.pt` - Medium model
- `yolov8l.pt` - Large model
- `yolov8x.pt` - Extra large model (en doğru)

## Dağıtım

### Production Kontrol Listesi

- [ ] `DEBUG=False` ayarla
- [ ] `ALLOWED_HOSTS` yapılandır
- [ ] Güçlü `SECRET_KEY` ayarla
- [ ] PostgreSQL veritabanı kullan
- [ ] Önbellekleme için Redis yapılandır
- [ ] SSL/TLS sertifikaları ayarla
- [ ] Firewall kurallarını yapılandır
- [ ] Otomatik yedekleme kur
- [ ] Loglama ve izleme yapılandır
- [ ] Celery worker'larını kur
- [ ] Nginx reverse proxy ile Gunicorn kullan

### Gunicorn

```bash
gunicorn yolowebapp2.wsgi:application \
  --config gunicorn_config.py
```

### Celery Worker'ları

```bash
# Celery worker'ı başlat
celery -A yolowebapp2 worker -l info

# Celery beat'i başlat (zamanlanmış görevler için)
celery -A yolowebapp2 beat -l info
```

## Sorun Giderme

### Veritabanı Bağlantı Sorunları

```bash
# PostgreSQL'in çalıştığını kontrol et
pg_isready

# Bağlantıyı test et
psql -U farmvision_user -d farmvision -h localhost
```

### Redis Bağlantı Sorunları

```bash
# Redis'in çalıştığını kontrol et
redis-cli ping

# PONG dönmeli
```

### GDAL Kurulum Sorunları

Windows kullanıcıları: Projeden uygun GDAL wheel'ini indirin veya OSGeo4W kullanın.

Linux kullanıcıları:
```bash
sudo apt-get install gdal-bin libgdal-dev
```

## Katkıda Bulunma

Katkıda bulunma kuralları ve pull request gönderme süreci için lütfen [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını okuyun.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Yazarlar

- FarmVision Ekibi

## Teşekkürler

- Ultralytics tarafından YOLOv8
- Drone görüntü işleme için WebODM
- Django topluluğu
- Tüm katkıda bulunanlar

## Destek

Destek için lütfen GitHub'da bir issue açın veya support@farmvision.com adresine e-posta gönderin.

## Değişiklik Günlüğü

Değişikliklerin listesi ve versiyon geçmişi için [CHANGELOG.md](CHANGELOG.md) dosyasına bakın.
