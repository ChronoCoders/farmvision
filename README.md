# Farm Vision System

## Overview

Farm Vision is a comprehensive agricultural management platform that combines AI-powered computer vision with geospatial mapping capabilities. The system provides fruit detection, disease identification, vegetation analysis, and project management tools for modern farming operations.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with Python
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Flask-Login for user session management
- **File Handling**: Local file storage with configurable upload directories
- **AI Processing**: YOLO v7 models for object detection and classification

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap-based responsive UI
- **Mapping**: Leaflet.js for interactive geospatial visualization
- **Charts**: Chart.js for data visualization and analytics
- **Language**: Turkish language interface with comprehensive form validation

### AI/ML Components
- **Detection Models**: Multiple YOLO configurations for different crop types
- **Disease Classification**: Specialized models for leaf disease identification
- **Vegetation Indices**: Comprehensive GeoTIFF processing for agricultural analysis
- **Ensemble Methods**: Multiple model inference for improved accuracy

## Key Components

### 1. User Management System
- User registration, authentication, and profile management
- Role-based access control with project ownership
- Session management with secure password handling

### 2. AI Detection Engine
- **Fruit Detection**: Multi-class fruit counting and classification
- **Disease Detection**: Leaf disease identification with recommendations
- **Tree Detection**: Agricultural asset mapping and counting
- **Weight Estimation**: Automated yield prediction algorithms

### 3. Project Management
- Farm and field organization with metadata tracking
- Image upload and processing workflows
- Results storage and historical analysis
- Geospatial project mapping

### 4. Geospatial Analysis
- **GeoTIFF Processing**: Orthomosaic image analysis
- **Vegetation Indices**: NDVI, GNDVI, EVI and 20+ other indices
- **Interactive Mapping**: Real-time visualization with zoom controls
- **Coordinate Systems**: Support for multiple projection systems

### 5. Data Processing Pipeline
- Image preprocessing and normalization
- Model inference with confidence scoring
- Result aggregation and statistical analysis
- Export capabilities for further analysis

## Data Flow

1. **Image Upload**: Users upload agricultural images through web interface
2. **Preprocessing**: Images are resized, normalized, and prepared for AI inference
3. **AI Processing**: YOLO models perform detection and classification
4. **Post-processing**: Results are aggregated, counted, and analyzed
5. **Visualization**: Results displayed through interactive charts and maps
6. **Storage**: All data persisted to database with file system backup

## External Dependencies

### AI/ML Libraries
- **PyTorch**: Deep learning framework for model inference
- **OpenCV**: Computer vision and image processing
- **NumPy/SciPy**: Numerical computing and scientific analysis
- **Rasterio**: Geospatial raster data processing

### Web Framework
- **Flask**: Core web application framework
- **SQLAlchemy**: Database ORM and migrations
- **Werkzeug**: WSGI utilities and security features
- **Gunicorn**: Production WSGI server

### Frontend Libraries
- **Bootstrap**: Responsive UI components
- **Leaflet.js**: Interactive mapping capabilities
- **Chart.js**: Data visualization and analytics
- **jQuery**: DOM manipulation and AJAX requests

### Geospatial Processing
- **GDAL/OGR**: Geospatial data abstraction library
- **Proj4**: Coordinate system transformations
- **GeoTIFF**: Georeferenced image format support

## Deployment Strategy

### Development Environment
- Flask development server with debug mode
- SQLite database for rapid prototyping
- Local file storage for images and results
- Hot reload for template and code changes

### Production Deployment
- Gunicorn WSGI server with multiple workers
- PostgreSQL database with connection pooling
- Nginx reverse proxy for static file serving
- Docker containerization for consistent deployments

### Scalability Considerations
- Horizontal scaling through load balancing
- Database read replicas for improved performance
- CDN integration for static asset delivery
- Caching layer for frequently accessed data

### Security Measures
- CSRF protection on all forms
- Secure file upload validation
- SQL injection prevention through ORM
- Session security with secure cookie configuration

## Changelog

- July 01, 2025. Initial setup
