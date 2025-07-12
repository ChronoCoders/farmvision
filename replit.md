# Farm Vision - AI-Powered Agricultural Analysis Platform

## Overview

Farm Vision is a comprehensive web application that combines AI-powered computer vision with agricultural mapping and analysis. The platform enables farmers and agricultural professionals to analyze crops, detect diseases, count fruits, and visualize farm data through interactive maps and vegetation indices.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (configurable to PostgreSQL via environment variables)
- **Authentication**: Flask-Login for user session management
- **File Handling**: Local file storage with configurable upload directories
- **AI Processing**: YOLO models integrated for object detection and disease recognition

### Frontend Architecture
- **Template Engine**: Jinja2 with responsive HTML templates
- **Styling**: Bootstrap framework with custom CSS
- **Interactive Maps**: Leaflet.js for GeoTIFF visualization and mapping
- **Charts**: Chart.js for data visualization
- **Language**: Turkish interface throughout the application

## Key Components

### 1. User Management System
- User registration and authentication
- Profile management with personal information
- Session-based access control
- Password reset functionality

### 2. Project Management
- Create and manage farm projects
- Associate projects with specific farms and fields
- Track project metadata (location, creation dates, etc.)
- Link projects to detection results and analyses

### 3. AI Detection System
- **Fruit Detection**: YOLO-based counting and classification
- **Disease Detection**: Leaf disease identification with recommendations
- **Multi-object Detection**: Batch processing capabilities
- **Model Ensemble**: Multiple AI models for improved accuracy

### 4. Geospatial Analysis
- **GeoTIFF Processing**: Handle large agricultural imagery
- **Vegetation Indices**: NDVI, EVI, SAVI and other agricultural indices
- **Interactive Mapping**: Real-time visualization of processed data
- **Histogram Analysis**: Statistical analysis of vegetation data

### 5. Data Storage
- **User Data**: Personal information and authentication
- **Project Data**: Farm and field information
- **Detection Results**: AI analysis results with metadata
- **File Management**: Organized storage for uploads and results

## Data Flow

1. **User Registration/Login**: Authentication through Flask-Login
2. **Project Creation**: Users create farm projects with metadata
3. **Image Upload**: Agricultural images uploaded to configured directories
4. **AI Processing**: YOLO models process images for detection/classification
5. **Result Storage**: Analysis results saved to database with file references
6. **Visualization**: Results displayed through charts, maps, and reports
7. **Export**: Processed data available for download and further analysis

## External Dependencies

### Core Framework Dependencies
- Flask and extensions (SQLAlchemy, Login)
- PyTorch for AI model inference
- OpenCV for image processing
- NumPy/SciPy for numerical computations

### Geospatial Dependencies
- Rasterio for GeoTIFF handling
- GDAL for geospatial operations
- Rio-tiler for raster processing
- Proj4 for coordinate transformations

### Frontend Dependencies
- Leaflet.js for interactive mapping
- Chart.js for data visualization
- Bootstrap for responsive design
- Font Awesome for icons

### AI Model Dependencies
- YOLO models for object detection
- Ultralytics for model management
- Custom trained models for agricultural applications

## Deployment Strategy

### Development Environment
- Flask development server with debug mode
- SQLite database for rapid prototyping
- Local file storage for uploads and results
- Environment variables for configuration

### Production Considerations
- Gunicorn WSGI server recommended
- PostgreSQL database for scalability
- Cloud storage integration capability
- SSL/TLS encryption for secure access
- Load balancing for high availability

### Configuration Management
- Environment-based configuration
- Separate settings for development/production
- Configurable file upload limits and directories
- Database connection string management

## Changelog
- July 03, 2025. Initial setup
- July 11, 2025. System audit and authentication improvements
  - Removed all mock/synthetic data from AI detection functions
  - Implemented authentic-only YOLO model system
  - Fixed PostgreSQL database integration
  - Enhanced error handling for missing model files
  - Updated UI with green header theme customization
- July 12, 2025. Critical debugging fixes and system hardening
  - Fixed circular import issues between app.py and error_handlers.py
  - Enhanced error handling with proper logging and exception management
  - Improved file upload validation with disk space and size checks
  - Added memory-efficient image preprocessing with fallback handling
  - Fixed division by zero protection in vegetation analysis calculations
  - Enhanced GeoTIFF reading with comprehensive error checking
  - Upgraded colormap application with bounds checking and vectorization
  - Added robust NDVI calculation with NaN/infinite value handling
  - Fixed health check endpoint with proper SQL text wrapping
  - Implemented comprehensive utility testing framework
  - Added memory monitoring with psutil for large file processing
  - Implemented timeout controls for long-running operations
  - Enhanced AI inference functions with proper exception handling
  - Added comprehensive input validation for all user parameters
  - Implemented file cleanup mechanisms for temporary processing files
  - Added logging throughout the system for debugging and monitoring

## User Preferences

Preferred communication style: Simple, everyday language.
**Critical Requirement**: 100% real AI data only - no mock, synthetic, or fallback data allowed.