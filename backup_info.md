# Farm Vision Backup Bilgileri

## Backup Tarihi: 30 Haziran 2025, 23:45

### Backup İçeriği:
- **Ana Dosyalar**: app.py, main.py, models.py
- **Rota Dosyaları**: routes/ klasörü (auth, detection, main, mapping)
- **Şablonlar**: templates/ klasörü (tüm HTML şablonları)
- **Statik Dosyalar**: static/ klasörü (CSS, JS, resimler)
- **Yardımcı Dosyalar**: utils/ klasörü (AI tespit, vegetation analizi)
- **Konfigürasyon**: pyproject.toml, replit.md

### Backup Dosyası:
`backups/farm_vision_backup_20250630_234520.tar.gz` (81 KB)

### Sistem Durumu:
- Uygulama çalışır durumda
- Tüm bağımlılıklar yüklü
- Flask + SQLAlchemy + AI modelleri aktif
- Türkçe arayüz tamamlandı

### Geri Yükleme Talimatları:
1. Backup dosyasını çıkart: `tar -xzf farm_vision_backup_YYYYMMDD_HHMMSS.tar.gz`
2. Dosyaları kopyala: `cp -r backup_icerigi/* ./`
3. Bağımlılıkları yükle: `uv sync`
4. Uygulamayı başlat: `gunicorn --bind 0.0.0.0:5000 main:app`

### Not:
- Kullanıcı verileri ve yüklenen dosyalar backup'a dahil değil
- Veritabanı dosyası (*.db) backup'a dahil değil
- __pycache__ ve geçici dosyalar hariç tutuldu