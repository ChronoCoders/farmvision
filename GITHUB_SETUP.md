# GitHub Repository Setup Guide

Bu rehber, FarmVision projesini GitHub'a yüklemek ve yapılandırmak için adım adım talimatlar içerir.

## İçindekiler

1. [Repository Oluşturma](#repository-oluşturma)
2. [Repository Ayarları](#repository-ayarları)
3. [Kod Yükleme](#kod-yükleme)
4. [Release Oluşturma](#release-oluşturma)
5. [Ek Yapılandırmalar](#ek-yapılandırmalar)

---

## Repository Oluşturma

### Adım 1: GitHub'da Yeni Repository Oluştur

1. GitHub'a giriş yapın
2. Sağ üst köşedeki `+` butonuna tıklayın
3. **New repository** seçin

### Adım 2: Repository Bilgilerini Doldurun

#### Repository Name (Zorunlu)
```
farmvision
```

#### Description (Önerilen - 160 karakter max)

**İngilizce:**
```
AI-powered agricultural analysis platform with YOLOv8 object detection, drone image processing, and real-time monitoring for precision farming.
```

**Türkçe:**
```
Yapay zeka destekli tarımsal analiz platformu. YOLOv8 nesne tespiti, drone görüntü işleme ve hassas tarım için gerçek zamanlı izleme.
```

#### Visibility
- [ ] Public (Herkes görebilir)
- [x] Private (Sadece siz ve ekibiniz görebilir)

**Önerilen:** Başlangıçta Private, hazır olduğunda Public'e çevirin

#### Initialize Repository
- [ ] ❌ **Add a README file** (Hayır - zaten var)
- [ ] ❌ **Add .gitignore** (Hayır - zaten var)
- [x] ✅ **Choose a license: MIT License** (Evet - veya sonra ekleyin)

### Adım 3: Create Repository

**Create repository** butonuna tıklayın.

---

## Repository Ayarları

### General Settings

1. **Settings** sekmesine gidin
2. **General** bölümünde yapılandırın:

#### Features
- [x] ✅ Issues
- [x] ✅ Projects (Optional)
- [ ] ❌ Wiki (README yeterli, ama isterseniz açabilirsiniz)
- [x] ✅ Discussions (Community için önerilir)

#### Pull Requests
- [x] ✅ Allow squash merging
- [x] ✅ Allow merge commits
- [x] ✅ Allow rebase merging
- [x] ✅ Automatically delete head branches

#### Archives
- [ ] ❌ Include Git LFS objects in archives (Kullanmıyorsanız kapalı)

### About (Repository Ana Sayfası)

1. Ana sayfada sağ üstteki **⚙️** (Settings) butonuna tıklayın
2. Aşağıdaki bilgileri ekleyin:

#### Description
```
AI-powered agricultural analysis platform with YOLOv8 object detection, drone image processing, and real-time monitoring for precision farming.
```

#### Website (Optional)
```
https://yourusername.github.io/farmvision
```

#### Topics (Tags)
Aşağıdaki topic'leri ekleyin (aralarında virgül olmadan):

```
agriculture
ai
machine-learning
yolov8
django
drone
computer-vision
precision-farming
object-detection
python
postgresql
redis
celery
webodm
gis
geospatial
orthophoto
pytorch
opencv
rest-api
remote-sensing
farm-management
turkish
image-processing
deep-learning
```

#### Include in the home page
- [x] ✅ Releases
- [x] ✅ Packages
- [ ] ❌ Deployments (Kullanmıyorsanız)

### Branch Protection Rules

1. **Settings** → **Branches** → **Add rule**
2. **Branch name pattern:** `main`
3. Aşağıdaki seçenekleri işaretleyin:

- [x] ✅ Require a pull request before merging
  - [x] ✅ Require approvals (1)
  - [x] ✅ Dismiss stale pull request approvals when new commits are pushed
- [x] ✅ Require status checks to pass before merging
  - [x] ✅ Require branches to be up to date before merging
- [x] ✅ Require conversation resolution before merging
- [x] ✅ Include administrators (Kendinizi de dahil etmek için)

**Not:** Solo çalışıyorsanız, bazı kuralları gevşetebilirsiniz.

### Social Preview

1. **Settings** → **General** → **Social preview**
2. **Edit** butonuna tıklayın
3. 1200x630 piksel boyutunda bir görsel yükleyin (opsiyonel)

Örnek görsel özellikleri:
- FarmVision logosu
- Proje screenshot'u
- Temiz, profesyonel tasarım

---

## Kod Yükleme

### İlk Defa Yükleme

```bash
# Repository'yi klonlayın (boş repo)
git clone https://github.com/ChronoCoders/farmvision.git

# Veya mevcut projenizi bağlayın
cd C:\farmvision

# Git başlat (eğer yoksa)
git init

# Remote ekle
git remote add origin https://github.com/ChronoCoders/farmvision.git

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: FarmVision v1.0.0

- Django 4.2.17 framework setup
- YOLOv8 object detection integration
- Drone project management system
- WebODM integration for orthophoto processing
- System monitoring dashboard
- RESTful API with Django REST Framework
- PostgreSQL database with PostGIS
- Redis caching and Celery task queue
- Docker and Docker Compose configuration
- Full Turkish language support
- Comprehensive documentation"

# Ana branch'i main olarak ayarla
git branch -M main

# GitHub'a yükle
git push -u origin main
```

### Mevcut Kod Varsa

```bash
cd C:\farmvision

# Remote kontrol et
git remote -v

# Remote yoksa ekle
git remote add origin https://github.com/ChronoCoders/farmvision.git

# Push et
git push -u origin main
```

---

## Release Oluşturma

### Method 1: Release Script Kullanarak (Önerilen)

```bash
# Script'i çalıştırılabilir yap (Linux/Mac)
chmod +x create_release.sh

# Release oluştur
./create_release.sh 1.0.0 stable

# Windows için
create_release.bat 1.0.0 stable
```

### Method 2: Manuel Tag Oluşturma

```bash
# Annotated tag oluştur
git tag -a v1.0.0 -m "Release v1.0.0 - Initial Release"

# Tag'i GitHub'a push et
git push origin v1.0.0

# Tüm tag'leri push et
git push origin --tags
```

### Method 3: GitHub Web Interface

1. Repository ana sayfasında **Releases** → **Create a new release**
2. **Choose a tag:** `v1.0.0` yazın ve "Create new tag: v1.0.0 on publish" seçin
3. **Release title:** `🚀 FarmVision v1.0.0 - Initial Release`
4. **Description:** `RELEASES.md` dosyasındaki v1.0.0 açıklamasını kopyalayın
5. **Assets:** İsterseniz ek dosyalar yükleyin (örn: wheels, sample data)
6. Seçenekler:
   - [x] ✅ **Set as the latest release**
   - [ ] ❌ **Set as a pre-release** (Beta/RC için işaretleyin)
   - [x] ✅ **Create a discussion for this release** (Optional)
7. **Publish release** butonuna tıklayın

### Method 4: GitHub CLI

```bash
# GitHub CLI yükle (eğer yoksa)
# https://cli.github.com/

# Login
gh auth login

# Release oluştur
gh release create v1.0.0 \
  --title "🚀 FarmVision v1.0.0 - Initial Release" \
  --notes-file RELEASES.md \
  --latest

# Pre-release oluştur
gh release create v1.0.0-beta.1 \
  --title "🧪 FarmVision v1.0.0 Beta 1" \
  --notes "Beta release for testing" \
  --prerelease

# Asset'lerle birlikte release
gh release create v1.0.0 \
  --title "🚀 FarmVision v1.0.0" \
  --notes-file RELEASES.md \
  requirements.txt \
  docker-compose.yml \
  .env.example
```

---

## Ek Yapılandırmalar

### GitHub Actions (CI/CD)

`.github/workflows/tests.yml` dosyası oluşturun:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgis/postgis:15-3.4
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y gdal-bin libgdal-dev

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Issue Templates

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g., Windows 10, Ubuntu 22.04]
 - Python Version: [e.g., 3.10.5]
 - Django Version: [e.g., 4.2.17]

**Additional context**
Add any other context about the problem here.
```

`.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Pull Request Template

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## How Has This Been Tested?
Describe the tests that you ran.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
```

### Labels (Etiketler)

Repository'nize bu label'ları ekleyin:

**Type:**
- `bug` - Hata raporları (kırmızı)
- `enhancement` - Yeni özellikler (mavi)
- `documentation` - Dokümantasyon (yeşil)
- `question` - Sorular (mor)

**Priority:**
- `priority: high` - Yüksek öncelik (kırmızı)
- `priority: medium` - Orta öncelik (sarı)
- `priority: low` - Düşük öncelik (mavi)

**Status:**
- `status: needs-review` - İnceleme bekliyor
- `status: in-progress` - Üzerinde çalışılıyor
- `status: blocked` - Engellenmiş

**Area:**
- `area: api` - API ile ilgili
- `area: frontend` - Frontend ile ilgili
- `area: backend` - Backend ile ilgili
- `area: ai` - AI/ML ile ilgili

### Security Policy

`.github/SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please email security@farmvision.com.

Do not create a public GitHub issue for security vulnerabilities.

We will respond within 48 hours and work with you to resolve the issue.
```

---

## Checklist

### Repository Kurulumu Tamamlandı Mı?

- [ ] Repository oluşturuldu
- [ ] Description ve topic'ler eklendi
- [ ] README.md yüklendi
- [ ] .gitignore yapılandırıldı
- [ ] LICENSE eklendi
- [ ] İlk commit push edildi
- [ ] Branch protection kuralları ayarlandı
- [ ] v1.0.0 release oluşturuldu
- [ ] Issue templates eklendi
- [ ] PR template eklendi
- [ ] GitHub Actions yapılandırıldı (opsiyonel)
- [ ] Security policy eklendi
- [ ] Labels oluşturuldu

### Son Kontroller

- [ ] Tüm linkler çalışıyor
- [ ] README'de username değiştirildi
- [ ] Görüntüler doğru yükleniyor
- [ ] Docker build çalışıyor
- [ ] CI/CD pipeline çalışıyor (varsa)

---

## Yardımcı Komutlar

```bash
# Tüm branch'leri göster
git branch -a

# Remote'ları göster
git remote -v

# Son commit'leri göster
git log --oneline -10

# Tag'leri listele
git tag -l

# Belirli bir tag'i kontrol et
git show v1.0.0

# Branch oluştur
git checkout -b feature/new-feature

# Pull request için push
git push origin feature/new-feature
```

---

## İletişim

Sorularınız için:
- Issue açın: https://github.com/ChronoCoders/farmvision/issues
- Email: support@farmvision.com
- Discussions: https://github.com/ChronoCoders/farmvision/discussions
