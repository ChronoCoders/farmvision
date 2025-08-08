"""
Error handling utilities for the Flask agricultural monitoring app
"""

import os
import logging
from functools import wraps
from flask import flash, redirect, request, url_for, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy

def safe_db_commit():
    """Safe database commit with rollback on error"""
    try:
        from app import db
        db.session.commit()
        return True
    except Exception as e:
        from app import db
        db.session.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        return False

def validate_form_inputs(required_fields, form_data):
    """Validate required form fields"""
    missing_fields = []
    for field in required_fields:
        if not form_data.get(field) or form_data.get(field).strip() == '':
            missing_fields.append(field)
    return missing_fields

def cleanup_temp_files(file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path) and ('/temp/' in path or '/tmp/' in path):
                os.remove(path)
        except Exception as e:
            current_app.logger.warning(f"Could not remove temp file {path}: {e}")

def handle_errors(f):
    """Decorator for comprehensive error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            flash('Dosya bulunamadı.', 'error')
            current_app.logger.error(f"File not found in {f.__name__}: {e}")
            return redirect(request.url)
        except ValueError as e:
            flash('Geçersiz veri girişi.', 'error')
            current_app.logger.error(f"Value error in {f.__name__}: {e}")
            return redirect(request.url)
        except PermissionError as e:
            flash('Dosya erişim izni hatası.', 'error')
            current_app.logger.error(f"Permission error in {f.__name__}: {e}")
            return redirect(request.url)
        except Exception as e:
            flash('Beklenmeyen bir hata oluştu.', 'error')
            current_app.logger.error(f"Unexpected error in {f.__name__}: {e}")
            return redirect(url_for('main.dashboard'))
    return decorated_function

def validate_app_config():
    """Validate required configuration settings"""
    from app import app
    required_configs = [
        'UPLOAD_FOLDER',
        'RESULTS_FOLDER',
        'SQLALCHEMY_DATABASE_URI'
    ]
    
    missing_configs = []
    for config in required_configs:
        if not app.config.get(config):
            missing_configs.append(config)
    
    # Check secret key separately
    if not app.secret_key:
        missing_configs.append('SECRET_KEY')
    
    if missing_configs:
        raise ValueError(f"Missing required configurations: {missing_configs}")

def setup_logging():
    """Setup minimal logging for clean output"""
    import logging
    from app import app
    
    # Set minimal logging levels
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) 
    logging.getLogger('rasterio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('root').setLevel(logging.WARNING)