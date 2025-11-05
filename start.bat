@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo  =============================================================================
echo                             FARMVISION BASLATILIYOR
echo  =============================================================================
echo.

REM Drone Animation Frame 1
cls
echo.
echo.
echo.
echo                                  .---.
echo                                 /     ^\.
echo                                 ^\.@-@./
echo                                 /`^\_/`^\.
echo                                //  _  ^\\
echo                               ^| ^\\     )^|_
echo                              /`^\_`^>  ^<_/ ^\.
echo                              ^\\__/'---'^\\__/
echo                         ___/  ^|       ^|  ^\\___
echo                        /                      ^\.
echo                  [====]  o ================= o  [====]
echo                        ^\\______________________/
echo.
echo                    [                              ] 10%%
timeout /t 1 /nobreak >nul

REM Frame 2
cls
echo.
echo.
echo                                      .---.
echo                                     /     ^\.
echo                                     ^\.@-@./
echo                                     /`^\_/`^\.
echo                                    //  _  ^\\
echo                                   ^| ^\\     )^|_
echo                                  /`^\_`^>  ^<_/ ^\.
echo                                  ^\\__/'---'^\\__/
echo                             ___/  ^|       ^|  ^\\___
echo                            /                      ^\.
echo                      [====]  o ================= o  [====]
echo                            ^\\______________________/
echo.
echo                    [========                      ] 25%%
timeout /t 1 /nobreak >nul

REM Frame 3
cls
echo.
echo                                          .---.
echo                                         /     ^\.
echo                                         ^\.@-@./
echo                                         /`^\_/`^\.
echo                                        //  _  ^\\
echo                                       ^| ^\\     )^|_
echo                                      /`^\_`^>  ^<_/ ^\.
echo                                      ^\\__/'---'^\\__/
echo                                 ___/  ^|       ^|  ^\\___
echo                                /                      ^\.
echo                          [====]  o ================= o  [====]
echo                                ^\\______________________/
echo.
echo.
echo                    [================              ] 50%%
timeout /t 1 /nobreak >nul

REM Frame 4
cls
echo                                              .---.
echo                                             /     ^\.
echo                                             ^\.@-@./
echo                                             /`^\_/`^\.
echo                                            //  _  ^\\
echo                                           ^| ^\\     )^|_
echo                                          /`^\_`^>  ^<_/ ^\.
echo                                          ^\\__/'---'^\\__/
echo                                     ___/  ^|       ^|  ^\\___
echo                                    /                      ^\.
echo                              [====]  o ================= o  [====]
echo                                    ^\\______________________/
echo.
echo.
echo.
echo                    [========================      ] 75%%
timeout /t 1 /nobreak >nul

REM Frame 5
cls
echo                                                  .---.
echo                                                 /     ^\.
echo                                                 ^\.@-@./
echo                                                 /`^\_/`^\.
echo                                                //  _  ^\\
echo                                               ^| ^\\     )^|_
echo                                              /`^\_`^>  ^<_/ ^\.
echo                                              ^\\__/'---'^\\__/
echo                                         ___/  ^|       ^|  ^\\___
echo                                        /                      ^\.
echo                                  [====]  o ================= o  [====]
echo                                        ^\\______________________/
echo.
echo.
echo.
echo                    [==============================] 100%%
timeout /t 1 /nobreak >nul

REM Clear and show main banner
cls
echo.
echo  ███████╗ █████╗ ██████╗ ███╗   ███╗██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
echo  ██╔════╝██╔══██╗██╔══██╗████╗ ████║██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
echo  █████╗  ███████║██████╔╝██╔████╔██║██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
echo  ██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
echo  ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║ ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
echo  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
echo  =============================================================================
echo  Yapay Zeka Destekli Tarimsal Goruntu Analiz Sistemi
echo  =============================================================================
echo.
echo  [BILGI] FarmVision baslatiliyor...
timeout /t 2 /nobreak >nul
echo.

echo  [SISTEM KONTROLU]
echo  Python Surumu:
python --version
echo  Django Surumu: 4.2.17
echo  PyTorch Surumu: 2.5.1
echo.

echo  [OZELLIKLER]
echo  - Meyve Tespiti ve Sayimi (YOLO v7)
echo  - Coklu Goruntu Toplu Isleme
echo  - Drone Ortofoto Harita Olusturma
echo  - Bitki Sagligi Analizi (NDVI)
echo  - Canli Agirlik Tahmini
echo.

echo  [MODULLER]
echo  - Detection: Tek/Coklu Goruntu Analizi
echo  - Drone Map: GeoTIFF Isleme ve Gorsellestirme
echo  - Admin Panel: Proje ve Veri Yonetimi
echo.

echo  [VERITABANI]
echo  Migration'lar calistiriliyor...
python manage.py migrate --noinput
echo.

echo  [SUNUCU]
echo  Django gelistirici sunucusu baslatiliyor...
echo  Uygulamaya erisim: http://127.0.0.1:8000
echo.
echo  Sunucuyu durdurmak icin CTRL+C basin
echo  ======================================================================
echo.

python manage.py runserver