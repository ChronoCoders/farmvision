# Farm Vision AI Application

## Overview

This is a Flask-based web application that provides AI-powered computer vision capabilities for agricultural analysis. The system combines YOLOv7 object detection models with agricultural image processing to detect and count fruits, identify leaf diseases, and provide vegetation analysis through various indices. The application includes user management, project organization, and real-time processing capabilities.

## System Architecture

The application follows a traditional Flask MVC architecture with the following key components:

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via environment variables
- **Authentication**: Flask-Login for session management
- **File Handling**: Local file storage with configurable upload directories
- **AI/ML Integration**: YOLOv7 models with PyTorch backend for object detection

### Frontend Architecture
- **Templates**: Jinja2 templating with modular component structure
- **Static Assets**: CSS, JavaScript, and image files served from static directory
- **Interactive Maps**: Leaflet.js integration for geospatial visualization
- **Charts**: Chart.js for data visualization

## Key Components

### Models (models.py)
- **User Model**: Handles user authentication and profile management
- **Project Model**: Organizes agricultural projects by farm, field, and location
- **DetectionResult Model**: Stores AI detection results with metadata

### Detection Engine
- **YOLOv7 Integration**: Custom detection scripts for fruit counting and disease identification
- **Multi-detection Support**: Batch processing capabilities for multiple images
- **Vegetation Indices**: NDVI, GLI, VARI and other agricultural indices calculation

### File Management
- **Upload System**: Handles image uploads with 100MB size limit
- **Result Storage**: Organized directory structure for processed images
- **Static Serving**: Efficient serving of detection results and visualizations

## Data Flow

1. **User Authentication**: Users log in through Flask-Login system
2. **Project Creation**: Users create projects with farm/field metadata
3. **Image Upload**: Agricultural images are uploaded and stored
4. **AI Processing**: YOLOv7 models process images for detection/classification
5. **Result Storage**: Detection results are saved with coordinates and counts
6. **Visualization**: Results are displayed through web interface with maps and charts

## External Dependencies

### Core Dependencies
- **Flask Ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login
- **AI/ML Stack**: PyTorch, YOLOv7, OpenCV, PIL
- **Geospatial**: GDAL, Rasterio, Leaflet.js
- **Data Processing**: NumPy, Pandas, SciPy

### Frontend Libraries
- **Mapping**: Leaflet.js with georaster support
- **Charts**: Chart.js for statistical visualization
- **UI Framework**: Custom CSS with responsive design

## Deployment Strategy

The application is configured for flexible deployment:

### Development Setup
- SQLite database for local development
- Debug mode enabled through main.py
- Local file storage in static directories

### Production Considerations
- Environment variable configuration for database URL
- ProxyFix middleware for reverse proxy deployment
- Configurable session secrets and upload limits
- Pool connection management for database reliability

### File Structure
```
static/
├── uploads/     # User uploaded images
├── results/     # AI processing results
└── detected/    # Detection visualization outputs
```

## Changelog
```
Changelog:
- June 30, 2025. Initial setup
- June 30, 2025. Completed full integration of uploaded files:
  * YOLO v7 model configurations (.yaml files) integrated
  * Advanced GDAL/rasterio histogram processing implemented  
  * Django components adapted to Flask (forms, models, views)
  * 15+ vegetation analysis algorithms from uploaded files
  * Corn disease detection with Turkish recommendations
  * Multi-fruit detection with weight coefficients (8 fruit types)
  * Added Turkish date/palm fruit detection (8-12 gram average)
  * Advanced colormap processing (RdYlGn_lut)
  * GeoTIFF processing with histogram analysis
  * All uploaded algorithms now functional in Flask app
- July 1, 2025. COMPLETE REAL AI SYSTEM TRANSITION:
  * Eliminated all mock/simulation data - now 100% authentic AI
  * Real YOLO v7 inference engine with PyTorch backend
  * Authentic fruit detection (no fake results)
  * Real corn disease detection with trained models
  * Genuine tree counting from drone imagery  
  * AI system status monitoring page added
  * Model loading system with fallback error handling
```

## User Preferences

Preferred communication style: Simple, everyday language.