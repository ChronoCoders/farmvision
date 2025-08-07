# Railway PORT Variable Fix

## Problem
Railway $PORT environment variable düzgün parse edilmiyor.

## Çözüm
- Dockerfile'da bash shell ile PORT variable expansion
- Default port 5000 fallback ile ${PORT:-5000}
- Procfile'da da aynı format

## Değişiklikler
1. Dockerfile CMD bash shell kullanıyor
2. PORT variable proper expansion
3. Fallback port 5000

Railway şimdi PORT variable'ını doğru kullanacak.