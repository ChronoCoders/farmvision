@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo  ══════════════════════════════════════════════════════════════════════
echo   WebODM Durdurma
echo  ══════════════════════════════════════════════════════════════════════
echo.

cd WebODM

echo [BİLGİ] WebODM durduruluyor...
docker-compose down

echo.
echo [OK] Tüm konteynerlar durduruldu.
echo.

cd ..
pause