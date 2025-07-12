import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Suppress rasterio boto3 warning
logging.getLogger('rasterio.session').setLevel(logging.ERROR)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///farm_vision.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULTS_FOLDER'] = 'static/results'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

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
