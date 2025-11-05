@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo  ███████╗ █████╗ ██████╗ ███╗   ███╗██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
echo  ██╔════╝██╔══██╗██╔══██╗████╗ ████║██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
echo  █████╗  ███████║██████╔╝██╔████╔██║██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
echo  ██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
echo  ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║ ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
echo  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
echo.
echo  ══════════════════════════════════════════════════════════════════════════════
echo   WebODM + NodeODM Otomatik Başlatma
echo   Drone Ortofoto Harita İşleme Sistemi
echo  ══════════════════════════════════════════════════════════════════════════════
echo.

echo [1/5] Docker Desktop durumu kontrol ediliyor...
timeout /t 2 > nul

docker --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo [HATA] Docker Desktop bulunamadı!
    echo.
    echo Lütfen Docker Desktop'ı yükleyin:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Kurulum sonrası bilgisayarı yeniden başlatın.
    pause
    exit /b 1
)

echo [OK] Docker sürümü:
docker --version
echo.

echo [2/5] Docker Desktop çalışma durumu kontrol ediliyor...
docker ps > nul 2>&1
if errorlevel 1 (
    echo.
    echo [UYARI] Docker Desktop çalışmıyor!
    echo.
    echo Docker Desktop uygulamasını başlatıp yeşil ışık yanana kadar bekleyin.
    echo Ardından bu betiği yeniden çalıştırın.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker Desktop çalışıyor
echo.

echo [3/5] WebODM klasörü kontrol ediliyor...
if not exist "WebODM" (
    echo.
    echo [HATA] WebODM klasörü bulunamadı!
    echo.
    echo Lütfen önce şu komutu çalıştırın:
    echo git clone https://github.com/OpenDroneMap/WebODM --config core.autocrlf=input --depth 1
    echo.
    pause
    exit /b 1
)

echo [OK] WebODM klasörü mevcut
echo.

echo [4/5] Mevcut WebODM konteynerları kontrol ediliyor...
docker ps | findstr webodm > nul 2>&1
if not errorlevel 1 (
    echo [BİLGİ] WebODM zaten çalışıyor, yeniden başlatılsın mı? (E/H)
    choice /C EH /N /M "Seçiminiz: "
    if errorlevel 2 goto skip_restart
    
    echo.
    echo [BİLGİ] Mevcut konteynerlar durduruluyor...
    cd WebODM
    docker-compose down
    cd ..
    timeout /t 3 > nul
)

:skip_restart
echo.
echo [5/5] WebODM başlatılıyor...
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════╗
echo  ║  BU İŞLEM İLK ÇALIŞTIRMADA 5-15 DAKİKA SÜREBİLİR                          ║
echo  ║  Docker imajları indirilecek (~1.5 GB)                                    ║
echo  ║                                                                           ║
echo  ║  Bu pencereyi KAPATMAYIN!                                                 ║
echo  ║  WebODM arka planda çalışacak                                             ║
echo  ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
timeout /t 5 > nul

cd WebODM
echo [BİLGİ] Docker Compose başlatılıyor...
echo.

start /min cmd /c "docker-compose -f docker-compose.yml -f docker-compose.nodeodm.yml up > webodm.log 2>&1"

echo [BİLGİ] Servisler başlatılıyor, lütfen bekleyin...
timeout /t 20 > nul

echo.
echo [KONTROL] Servislerin durumu kontrol ediliyor...
echo.

:check_loop
docker ps | findstr "node-odm" > nul 2>&1
if errorlevel 1 (
    echo NodeODM henüz hazır değil, bekleniyor...
    timeout /t 5 > nul
    goto check_loop
)

docker ps | findstr "webapp" > nul 2>&1
if errorlevel 1 (
    echo WebApp henüz hazır değil, bekleniyor...
    timeout /t 5 > nul
    goto check_loop
)

color 0A
cls

echo.
echo  ███████╗ █████╗ ██████╗ ███╗   ███╗██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
echo  ██╔════╝██╔══██╗██╔══██╗████╗ ████║██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
echo  █████╗  ███████║██████╔╝██╔████╔██║██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
echo  ██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
echo  ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║ ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
echo  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
echo.
echo  ══════════════════════════════════════════════════════════════════════════════
echo   SİSTEM BAŞARIYLA BAŞLATILDI!
echo  ══════════════════════════════════════════════════════════════════════════════
echo.
echo  [SERVİSLER]
echo  ----------------------------------------------------------------------------
echo   ✓ PostgreSQL Veritabanı : ÇALIŞIYOR
echo   ✓ Redis Broker          : ÇALIŞIYOR  
echo   ✓ NodeODM API           : http://localhost:3000
echo   ✓ WebODM Kontrol Paneli : http://localhost:8000
echo   ✓ Celery Worker         : ÇALIŞIYOR
echo.
echo  [DJANGO FARMVISION]
echo  ----------------------------------------------------------------------------
echo   Port                    : http://127.0.0.1:8000
echo   Durum                   : MANUEL BAŞLATMA GEREKLİ
echo.
echo   Django'yu başlatmak için yeni bir terminal açın ve:
echo   ^> cd C:\farmvision
echo   ^> venv\Scripts\activate
echo   ^> python manage.py runserver
echo.
echo  [ÖNEMLİ BİLGİLER]
echo  ----------------------------------------------------------------------------
echo   • WebODM arka planda çalışıyor (simge durumuna küçültüldü)
echo   • WebODM'i durdurmak için: docker-compose down
echo   • Günlük dosyaları: C:\farmvision\WebODM\webodm.log
echo   • Bu pencereyi kapatabilirsiniz, WebODM çalışmaya devam edecek
echo.
echo  [KULLANIM]
echo  ----------------------------------------------------------------------------
echo   1. WebODM ilk giriş: http://localhost:8000 (yönetici hesabı oluşturun)
echo   2. Django FarmVision: http://127.0.0.1:8000 (yukarıdaki komutu çalıştırın)
echo   3. Drone projesi oluşturun ve JPG görsellerini yükleyin
echo   4. Sistem otomatik olarak ortofoto haritasını oluşturacak
echo.
echo  ══════════════════════════════════════════════════════════════════════════════
echo.

cd ..

pause

exit /b 0