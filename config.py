"""
Environment Configuration Module for Farm Vision
Centralized configuration management using environment variables
"""
import os
import logging
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv  # type: ignore[import-untyped]
    # Look for .env file in current directory and parent directories
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        logging.info(f"Loaded environment configuration from {env_path.absolute()}")
    else:
        # Try to find .env in parent directory
        parent_env = Path('../.env')
        if parent_env.exists():
            load_dotenv(parent_env)
            logging.info(f"Loaded environment configuration from {parent_env.absolute()}")
        else:
            pass  # Quietly use system environment variables
except ImportError:
    # In production, python-dotenv should be mandatory
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env == 'production':
        raise RuntimeError(
            "PRODUCTION ERROR: python-dotenv is required in production environment. "
            "Install with: pip install python-dotenv"
        )
    else:
        pass  # Quietly use system environment variables


class Config:
    """Base configuration class with environment variable defaults"""
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'true').lower() == 'true'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    
    # Application Configuration
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    
    # Database Configuration  
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,  # Recycle connections before timeout
        "pool_pre_ping": True,  # Verify connections before use
        "pool_timeout": 20,  # Connection timeout
        "max_overflow": 10,  # Additional connections beyond pool_size
        "pool_size": 5,  # Base connection pool size
        "connect_args": {
            "sslmode": "require",  # Force SSL connection
            "connect_timeout": 10,  # Connection establishment timeout
            "application_name": "farm_vision"  # Identify our application
        }
    }
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    RESULTS_FOLDER = os.environ.get('RESULTS_FOLDER', 'static/results')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', str(50 * 1024 * 1024)))  # 50MB default
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,tiff,tif,geotiff').split(','))
    
    # AI Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', 'detection_models')
    YOLO_CONFIDENCE_THRESHOLD = float(os.environ.get('YOLO_CONFIDENCE_THRESHOLD', '0.25'))
    YOLO_IOU_THRESHOLD = float(os.environ.get('YOLO_IOU_THRESHOLD', '0.45'))
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/farm_vision.log')
    
    @classmethod
    def validate_required_config(cls) -> None:
        """Validate that all required configuration is present"""
        required_vars = []
        
        # Check for required security configuration
        if not cls.SECRET_KEY:
            required_vars.append('SECRET_KEY')
            
        # Check for database configuration
        if not cls.SQLALCHEMY_DATABASE_URI:
            required_vars.append('DATABASE_URL or SQLALCHEMY_DATABASE_URI')
        
        if required_vars:
            raise RuntimeError(
                f"CRITICAL CONFIGURATION ERROR: Required environment variables missing: {', '.join(required_vars)}.\n"
                f"Please set these variables in your .env file or system environment.\n"
                f"Copy .env.example to .env and configure your values.\n"
                f"Generate SECRET_KEY with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
    
    @classmethod
    def setup_directories(cls) -> None:
        """Create required directories if they don't exist"""
        directories = [
            cls.UPLOAD_FOLDER,
            cls.RESULTS_FOLDER,
            cls.MODEL_PATH,
            Path(cls.LOG_FILE).parent if cls.LOG_FILE else None
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup application logging based on configuration"""
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)
        
        # Create log directory if needed
        if cls.LOG_FILE:
            Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging format
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Setup handlers
        handlers: list = [logging.StreamHandler()]  # Console handler
        
        if cls.LOG_FILE:
            handlers.append(logging.FileHandler(cls.LOG_FILE))  # File handler
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers,
            force=True
        )
        
        # Suppress verbose third-party logging in production
        if cls.FLASK_ENV == 'production':
            logging.getLogger('rasterio.session').setLevel(logging.ERROR)
            logging.getLogger('matplotlib').setLevel(logging.ERROR)
            logging.getLogger('PIL').setLevel(logging.ERROR)


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'
    
    # Development database fallback
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///farm_vision_dev.db'


class ProductionConfig(Config):
    """Production environment configuration with strict requirements"""
    DEBUG = False
    FLASK_ENV = 'production'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    # Railway.app specific optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,  # Recycle connections before timeout
        "pool_pre_ping": True,  # Verify connections before use
        "pool_timeout": 20,  # Connection timeout
        "max_overflow": 20,  # Additional connections for Railway scaling
        "pool_size": 10,  # Base connection pool size for Railway
        "connect_args": {
            "sslmode": "require",  # Force SSL connection
            "connect_timeout": 10,  # Connection establishment timeout
            "application_name": "farm_vision_railway"  # Identify our Railway app
        }
    }
    
    @classmethod
    def validate_required_config(cls) -> None:
        """Enhanced validation for production environment"""
        super().validate_required_config()
        
        # Production-specific validations
        if cls.DEBUG:
            raise RuntimeError("SECURITY ERROR: DEBUG mode cannot be enabled in production!")
            
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
            raise RuntimeError(
                "SECURITY ERROR: Production requires a strong SECRET_KEY (32+ characters). "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
            
        if 'sqlite' in (cls.SQLALCHEMY_DATABASE_URI or ''):
            logging.warning("WARNING: Using SQLite in production is not recommended. Consider PostgreSQL.")


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    

# Configuration mapping
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(environment: Optional[str] = None) -> type[Config]:
    """Get configuration class based on environment"""
    if not environment:
        environment = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_mapping.get(environment or 'development', DevelopmentConfig)
    return config_class


def initialize_config(app, environment: Optional[str] = None):
    """Initialize Flask app with environment configuration"""
    config = get_config(environment)
    
    # Validate configuration
    config.validate_required_config()
    
    # Setup logging first
    config.setup_logging()
    
    # Setup required directories
    config.setup_directories()
    
    # Configure Flask app
    app.config.from_object(config)
    
    # CRITICAL: Explicitly set secret key for Flask-WTF CSRF
    if config.SECRET_KEY:
        app.secret_key = config.SECRET_KEY
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['WTF_CSRF_SECRET_KEY'] = config.WTF_CSRF_SECRET_KEY or config.SECRET_KEY
    else:
        raise RuntimeError("SECRET_KEY is required but not found in environment variables")
    
    logging.info(f"Initialized Farm Vision with {config.__name__}")
    logging.info(f"Environment: {config.FLASK_ENV}")
    logging.info(f"Database: {config.SQLALCHEMY_DATABASE_URI}")
    logging.info(f"Upload folder: {config.UPLOAD_FOLDER}")
    logging.info(f"Model path: {config.MODEL_PATH}")
    logging.info(f"SECRET_KEY configured: {'Yes' if config.SECRET_KEY else 'No'}")
    
    return config