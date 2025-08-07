import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Import centralized configuration
from config import initialize_config

class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create the app
app = Flask(__name__)

# Initialize configuration from environment
config = initialize_config(app)

# Apply ProxyFix for proper HTTPS handling
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask extensions with app
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

# Configure Flask-Login
login_manager.login_view = 'auth.login'  # type: ignore[assignment]
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    from utils.database_helpers import safe_first_query
    try:
        user_query = User.query.filter(User.id == int(user_id))
        return safe_first_query(user_query, error_default=None)
    except Exception as e:
        logging.error(f"User loader error: {e}")
        return None

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('static/detected', exist_ok=True)
os.makedirs('static/convertor', exist_ok=True)

with app.app_context():
    # Import models and routes
    import models
    from utils.error_handlers import setup_logging, validate_app_config
    
    # Setup logging and validate configuration
    setup_logging()
    validate_app_config()
    from routes.main import main_bp
    from routes.detection import detection_bp
    from routes.mapping import mapping_bp
    from routes.auth import auth_bp
    from routes.api import api
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(detection_bp, url_prefix='/detection')
    app.register_blueprint(mapping_bp, url_prefix='/mapping')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api)
    
    # Create all database tables
    db.create_all()
