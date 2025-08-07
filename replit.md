# Farm Vision - AI-Powered Agricultural Analysis Platform

## Overview

Farm Vision is a comprehensive web application combining AI-powered computer vision with agricultural mapping and analysis. It enables farmers and agricultural professionals to analyze crops, detect diseases, count fruits, and visualize farm data through interactive maps and vegetation indices. The platform aims to provide advanced, data-driven insights for improved agricultural productivity and decision-making.

## User Preferences

Preferred communication style: Simple, everyday language.
**Critical Requirement**: 100% real AI data only - no mock, synthetic, or fallback data allowed.

## System Architecture

**Backend:**
- **Framework**: Flask with SQLAlchemy ORM.
- **Database**: SQLite (default), configurable to PostgreSQL.
- **Authentication**: Flask-Login for user session management.
- **AI Processing**: Integrated YOLO models for object detection and disease recognition.
- **File Handling**: Local storage for uploads.

**Frontend:**
- **Template Engine**: Jinja2.
- **Styling**: Bootstrap with custom CSS.
- **Interactive Maps**: Leaflet.js for GeoTIFF visualization.
- **Charts**: Chart.js for data visualization.
- **Language**: Turkish interface.

**Core Features:**
- **User Management**: Registration, authentication, profile management, and password reset.
- **Project Management**: Creation, tracking, and management of farm projects, linking them to analyses.
- **AI Detection**: YOLO-based fruit counting, disease identification, and multi-object detection with model ensemble capabilities.
- **Geospatial Analysis**: Processing of large agricultural imagery (GeoTIFF), calculation of vegetation indices (NDVI, EVI, SAVI), interactive mapping, and histogram analysis.
- **Data Storage**: Secure storage for user, project, and AI detection results.
- **Analytics Dashboard**: Professional-grade analytics with authentic data visualization, including yield data, confidence metrics, fruit distribution, and activity trends.
- **Reporting System**: Generation of detailed reports for fruit detection, vegetation analysis, with filtering options and multiple formats.
- **UI/UX**: Responsive design with a consistent color scheme, professional layouts, enhanced navigation, and improved accessibility.

## External Dependencies

- **Core Frameworks**: Flask, PyTorch, OpenCV, NumPy, SciPy.
- **Geospatial**: Rasterio, GDAL, Rio-tiler, Proj4.
- **Frontend Libraries**: Leaflet.js, Chart.js, Bootstrap, Font Awesome.
- **AI Models**: YOLO models (e.g., via Ultralytics) and custom-trained agricultural models.
- **Configuration**: python-dotenv for environment variable management.

## Required Environment Variables

The following environment variables must be configured for production deployment:

### Critical Security Variables
- `SECRET_KEY`: Strong random key (32+ characters) for Flask sessions and CSRF protection
- `WTF_CSRF_SECRET_KEY`: Separate CSRF token signing key for additional security

### Database Configuration  
- `DATABASE_URL` or `SQLALCHEMY_DATABASE_URI`: Full database connection string

### Application Settings
- `FLASK_ENV`: Environment mode (development/production/testing)
- `DEBUG`: Enable/disable debug mode (false in production)
- `LOG_LEVEL`: Logging verbosity (INFO/WARNING/ERROR/DEBUG)

### File Upload Configuration
- `UPLOAD_FOLDER`: Directory for uploaded files (default: static/uploads)  
- `RESULTS_FOLDER`: Directory for processing results (default: static/results)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 50MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file extensions

### AI Model Configuration
- `MODEL_PATH`: Directory containing YOLO model files (default: detection_models)
- `YOLO_CONFIDENCE_THRESHOLD`: AI detection confidence threshold (default: 0.25)
- `YOLO_IOU_THRESHOLD`: Non-maximum suppression threshold (default: 0.45)

Copy `.env.example` to configure your environment variables. Generate secure keys with:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

## Recent Critical Updates

- **August 07, 2025**: Enterprise-Level Template Security Audit - Complete templates/ Folder Hardening
  - **SECURITY CRITICAL**: Comprehensive client-side validation and secure template implementation across all HTML templates
  - **Template Security Implementation**:
    - Added comprehensive client-side validation for all forms with required, min/max length, pattern validation
    - Implemented safe dictionary access using .get() methods replacing direct dict access throughout templates
    - Enhanced CSRF protection with both form.hidden_tag() and csrf_token() fallback support
    - Added professional error handling for None/empty values in all data display sections
  - **Authentication Templates Enhancement**:
    - login.html: Added dual form support (Flask-WTF + manual), real-time validation feedback, comprehensive input validation
    - register.html: Implemented password strength indicator, live password matching, enhanced field validation with Turkish patterns
    - Added proper error message display and client-side validation with Turkish localization
  - **Dashboard & Project Templates Security**:
    - dashboard.html: Safe stats access with .get() methods, prevented None reference crashes
    - project_detail.html: CSRF token for delete forms, safe detection_stats access with fallbacks
    - Enhanced data visualization with proper null checks and informative empty states
  - **Report & Analysis Templates Protection**:
    - vegetation_report.html: Comprehensive null checks for report data, algorithm stats, and analysis arrays
    - Added informative empty states instead of crashes when data unavailable
    - Safe mathematical operations with NaN/inf protection in progress bars and statistics
  - **Project Management Templates Enhancement**:
    - new_project.html & edit_project.html: Added CSRF tokens, comprehensive validation, character counting
    - Real-time validation feedback with Turkish error messages and professional user guidance

- **August 07, 2025**: Enterprise-Level Security Audit - Complete routes/ Folder Security Hardening
  - **SECURITY CRITICAL**: Comprehensive security audit and enhancement of all route blueprints based on detailed user security findings
  - **routes/auth.py Production Hardening**:
    - Implemented Flask-WTF forms with built-in CSRF token validation using form.validate_on_submit()
    - Added production-grade password regex validation requiring uppercase, lowercase, digits, and special characters (@$!%*?&)
    - Enhanced input validation with comprehensive None checks and type safety
    - Added open redirect vulnerability protection for next_page parameter validation
    - Implemented secure user lookup with case-insensitive search and enhanced duplicate checking
    - Added comprehensive error logging with generic error messages to prevent username enumeration
  - **routes/mapping.py Security Enhancement**:
    - Replaced broad try/except blocks with specific exception handling (FileNotFoundError, ValueError, PermissionError)
    - Converted all string redirects to url_for() calls for route safety and maintainability
    - Added comprehensive file cleanup on errors to prevent storage leaks
    - Enhanced error messages with Turkish localization and specific guidance
  - **routes/detection.py Turkish Localization & Enhanced User Feedback**:
    - Converted all English error messages to professional Turkish localization
    - Implemented informative feedback for empty detection results instead of silent failures
    - Added enhanced user guidance for failed detections with actionable suggestions
    - Implemented specific exception handling with proper error categorization
    - Enhanced confidence score validation and display formatting

- **August 07, 2025**: Production-Grade Security Hardening - utils/ Folder Complete Audit & Enhancement
  - **SECURITY CRITICAL**: Comprehensive security, type safety, and performance improvements across utils/ folder
  - **yolo_detection.py Hardening**:
    - Added full type annotations (Optional, Union, Dict, List, Any, Tuple) throughout all functions
    - Implemented comprehensive input validation with isinstance() checks and guard clauses
    - Enhanced file path validation with os.path.exists(), file permissions, and size checks
    - Replaced all print() statements with professional logger.error/warning/info calls
    - Added robust error handling for torch.load() operations and model loading failures
    - Implemented NoneType validation for all return values and intermediate variables
    - Added comprehensive OpenCV image loading validation with dimension and format checks
  - **vegetation_analysis.py Hardening**:
    - Complete type safety implementation with proper type hints and return annotations
    - Enhanced GeoTIFF support with rasterio error handling and band validation
    - Comprehensive numpy array validation with finite value checks and shape validation
    - Professional logging standardization replacing all direct print() usage
    - Added guard clauses for NoneType scenarios and mathematical edge cases
    - Implemented safe division operations with epsilon protection and NaN/inf handling
    - Enhanced calculate_statistics_from_geotiff() with robust raster.read() error recovery
  - **Database Connection Resilience**:
    - Created utils/database_helpers.py with retry logic and exponential backoff
    - Implemented comprehensive PostgreSQL connection error handling
    - Added safe query wrappers (safe_count_query, safe_all_query, safe_first_query)
    - Enhanced connection pooling parameters with SSL requirements and timeouts
  - **Professional Header Design**:
    - Completely redesigned navigation with modern gradient background and professional styling
    - Implemented responsive dropdown menus with descriptions and color-coded icons
    - Added user profile management with proper avatar and menu organization
    - Created production-grade CSS with hover effects, transitions, and mobile responsiveness

- **August 07, 2025**: Robust YOLO Error Handling Implementation - Production-Grade Fallback Logic
  - **RELIABILITY CRITICAL**: Implemented comprehensive error handling across all YOLO detection functions
  - Added safe fallback logic when AI model files (.pt) are missing - prevents system crashes
  - Implemented multi-layer validation: file existence, model availability, size verification
  - Added graceful degradation: authentic empty results instead of system failures
  - Enhanced logging with clear warnings for missing models without suppressing real errors
  - Created `create_safe_detection_result()` helper for consistent error responses
  - Added `check_model_availability()` function with file size validation (10MB+ for authentic models)
  - Protected all 3 core detection functions: `detect_fruits_yolo()`, `detect_leaf_disease_corn()`, `detect_trees_from_drone()`
  - Maintained 100% authentic data policy - no synthetic fallbacks, clear error messaging when models unavailable
  - System now handles missing YOLO models gracefully while maintaining production stability

- **August 07, 2025**: Environment Configuration System - Production-Grade Configuration Management
  - **SECURITY CRITICAL**: Implemented comprehensive environment configuration using python-dotenv
  - Added centralized configuration management in config.py with environment-specific settings
  - Eliminated all hardcoded secrets, paths, and environment-specific values from codebase
  - Created secure configuration classes: DevelopmentConfig, ProductionConfig, TestingConfig
  - Added comprehensive validation for required environment variables with clear error messages
  - Implemented automatic directory creation for uploads, results, models, and logs
  - Added production security validation: DEBUG mode blocking, strong SECRET_KEY requirements
  - Created .env.example template with all required configuration variables
  - Enhanced file upload security to use configurable limits and extensions
  - Production systems now enforce secure configuration standards and fail fast on misconfigurations