# FarmVision - GitHub'a Yükleme Hızlı Başlangıç

Bu dosya, FarmVision projesini GitHub'a hızlıca yüklemek için kısa ve öz talimatlar içerir.

## 🚀 5 Dakikada GitHub'a Yükleme

### 1. GitHub Repository Oluştur

1. https://github.com/new adresine git
2. **Repository name:** `farmvision`
3. **Description:**
   ```
   AI-powered agricultural analysis platform with YOLOv8 object detection, drone image processing, and real-time monitoring for precision farming.
   ```
4. **Public** veya **Private** seç
5. ❌ README, .gitignore, LICENSE ekleme (zaten var)
6. **Create repository**

### 2. Proje Bilgilerini Güncelle

**README.md** dosyasını aç ve değiştir:
- `yourusername` → gerçek GitHub kullanıcı adınız
- `support@farmvision.com` → gerçek email adresiniz (opsiyonel)

**Değiştirilmesi gereken dosyalar:**
- README.md (7 yerde)
- README_TR.md (3 yerde)
- RELEASES.md (5 yerde)
- GITHUB_SETUP.md (7 yerde)
- CONTRIBUTING.md (3 yerde)

**Hızlı değiştirme (Find & Replace):**
```
Bul: yourusername
Değiştir: gerçek-kullanici-adiniz

Bul: YOUR_USERNAME
Değiştir: gerçek-kullanici-adiniz
```

### 3. Kodu GitHub'a Yükle

```bash
cd C:\farmvision

# Git başlat (eğer yoksa)
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: FarmVision v1.0.0"

# Branch'i main yap
git branch -M main

# Remote ekle (ChronoCoders yerine kendi kullanıcı adınızı yazın)
git remote add origin https://github.com/ChronoCoders/farmvision.git

# Push et
git push -u origin main
```

### 4. Repository Ayarlarını Düzenle

1. Repository ana sayfasında sağ üstteki **⚙️** (About settings) tıkla
2. **Description** ekle (yukarıdaki metni kullan)
3. **Topics** ekle:
   ```
   agriculture ai machine-learning yolov8 django drone computer-vision
   precision-farming object-detection python postgresql redis celery
   ```
4. **✅ Releases** seçeneğini aktif et

### 5. İlk Release'i Oluştur

#### Option A: Web Interface (En Kolay)

1. Repository'de **Releases** → **Create a new release**
2. **Tag:** `v1.0.0` (yeni tag oluştur)
3. **Title:** `🚀 FarmVision v1.0.0 - Initial Release`
4. **Description:** `RELEASES.md` dosyasındaki v1.0.0 bölümünü kopyala-yapıştır
5. **✅ Set as the latest release** işaretle
6. **Publish release**

#### Option B: Script Kullan (Otomatik)

**Windows:**
```bash
create_release.bat 1.0.0 stable
```

**Linux/Mac:**
```bash
chmod +x create_release.sh
./create_release.sh 1.0.0 stable
```

#### Option C: GitHub CLI (Gelişmiş)

```bash
# GitHub CLI yükle: https://cli.github.com/
gh auth login

# Release oluştur
gh release create v1.0.0 \
  --title "🚀 FarmVision v1.0.0 - Initial Release" \
  --notes-file RELEASES.md \
  --latest
```

---

## ✅ Tamamlandı!

Repository'niz artık hazır! 🎉

**Repository URL:**
```
https://github.com/ChronoCoders/farmvision
```

---

## 📋 Sonraki Adımlar (Opsiyonel)

### Branch Protection Ekle

1. **Settings** → **Branches** → **Add rule**
2. **Branch name pattern:** `main`
3. **✅ Require a pull request before merging**
4. **Save changes**

### Issue Templates Ekle

`.github/ISSUE_TEMPLATE/bug_report.md` dosyası oluştur (detaylar GITHUB_SETUP.md'de)

### GitHub Actions Ekle

`.github/workflows/tests.yml` dosyası oluştur (detaylar GITHUB_SETUP.md'de)

### README Badge'leri Ekle

README.md'nin en üstüne ekle:

```markdown
# FarmVision

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2.17-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-stable-success.svg)
```

---

## 🆘 Sorun mu Yaşıyorsunuz?

### Git hatası: "fatal: not a git repository"
```bash
cd C:\farmvision
git init
```

### Remote already exists
```bash
git remote remove origin
git remote add origin https://github.com/ChronoCoders/farmvision.git
```

### Authentication hatası
```bash
# GitHub Personal Access Token oluşturun:
# Settings → Developer settings → Personal access tokens → Generate new token
# Şifre yerine bu token'ı kullanın
```

### Dosya çok büyük hatası
```bash
# .gitignore'a eklenmiş mi kontrol edin
git rm --cached dosya-adi
```

---

## 📚 Detaylı Dokümantasyon

Daha fazla bilgi için:
- **GITHUB_SETUP.md** - Tam kurulum rehberi
- **RELEASES.md** - Release oluşturma detayları
- **CONTRIBUTING.md** - Katkıda bulunma rehberi

---

## 🎯 Özet Komutlar

```bash
# 1. Repository'yi klonla veya başlat
git clone https://github.com/ChronoCoders/farmvision.git
# veya
cd C:\farmvision && git init

# 2. İlk commit
git add .
git commit -m "Initial commit: FarmVision v1.0.0"

# 3. Push
git branch -M main
git remote add origin https://github.com/ChronoCoders/farmvision.git
git push -u origin main

# 4. Tag ve release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Release oluştur (Web UI'da)
# https://github.com/ChronoCoders/farmvision/releases/new?tag=v1.0.0
```

**Tebrikler! Projeniz GitHub'da! 🚀**
