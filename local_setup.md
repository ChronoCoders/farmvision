# Farm Vision - Lokal Geliştirme Kurulumu

## Yöntem 1: pyproject.toml ile (Önerilen)

```bash
# Proje klasörüne git
cd farm-vision

# Editable mode ile kur
pip install -e .

# Veya development dependencies ile
pip install -e ".[dev]"
```

## Yöntem 2: requirements.txt ile (Klasik)

Eğer requirements.txt tercih ediyorsanız:

```bash
# pyproject.toml'dan requirements.txt oluştur
pip-compile pyproject.toml

# Veya manuel requirements.txt
pip install -r requirements.txt
```

## Minimal requirements.txt

```txt
flask>=3.1.1
flask-login>=0.6.3
flask-sqlalchemy>=3.1.1
flask-wtf>=1.2.2
gunicorn>=23.0.0
torch>=2.7.1
torchvision>=0.22.1
opencv-python>=4.11.0
numpy>=2.3.1
pillow>=11.2.1
rasterio>=1.4.3
sqlalchemy>=2.0.41
psycopg2-binary>=2.9.10
```

## Virtual Environment

```bash
# Virtual environment oluştur
python -m venv venv

# Aktif et (Linux/Mac)
source venv/bin/activate

# Aktif et (Windows)
venv\Scripts\activate

# Kütüphaneleri yükle
pip install -e .
```

## Geliştirme Serveri

```bash
# Flask development server
python main.py

# Veya
flask run --host=0.0.0.0 --port=5000

# Production test için
gunicorn --bind 0.0.0.0:5000 main:app
```

## Environment Variables

```bash
# .env dosyası oluştur
echo "SESSION_SECRET=your-secret-key" > .env
echo "DATABASE_URL=sqlite:///farm_vision.db" >> .env

# Veya export ile
export SESSION_SECRET="your-secret-key"
export DATABASE_URL="sqlite:///farm_vision.db"
```

## Sonuç

- **Modern projeler**: pyproject.toml
- **Eski projeler**: requirements.txt
- **Farm Vision**: Her ikisi de çalışır
- **Replit**: Otomatik pyproject.toml kullanır
- **Lokal**: Tercihinize göre, ikisi de desteklenir