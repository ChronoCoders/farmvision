#!/bin/bash
set -e

# Set default port if not provided
export PORT=${PORT:-5000}

echo "Starting Farm Vision on port $PORT"

# Initialize database
python -c "
from app import app, db
with app.app_context():
    try:
        db.create_all()
        print('Database tables created successfully')
    except Exception as e:
        print(f'Database initialization error: {e}')
"

# Start the application
exec gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    main:app