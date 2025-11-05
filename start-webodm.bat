@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo  ══════════════════════════════════════════════════════════════════════
echo   WebODM Hızlı Başlatma
echo  ══════════════════════════════════════════════════════════════════════
echo.

cd WebODM

docker ps | findstr "node-odm" > nul 2>&1
if not errorlevel 1 (
    echo [BİLGİ] WebODM zaten çalışıyor!
    echo.
    echo  NodeODM : http://localhost:3000
    echo  WebODM  : http://localhost:8000
    echo.
    pause
    exit /b 0
)

echo [BİLGİ] WebODM başlatılıyor... (15-30 saniye)
docker-compose -f docker-compose.yml -f docker-compose.nodeodm.yml up -d

timeout /t 20 > nul

color 0A
echo.
echo [OK] WebODM başlatıldı!
echo.
echo  NodeODM : http://localhost:3000
echo  WebODM  : http://localhost:8000
echo.

cd ..
pause