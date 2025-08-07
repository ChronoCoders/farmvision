#!/bin/bash
set -e

# Set default port if PORT is not set
if [ -z "$PORT" ]; then
    export PORT=5000
fi

echo "Starting Farm Vision on port $PORT"

# Start gunicorn
exec /opt/venv/bin/gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    main:app