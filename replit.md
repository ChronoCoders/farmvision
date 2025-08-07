# Farm Vision - AI-Powered Agricultural Analysis Platform

## Overview

Farm Vision is a comprehensive web application that combines AI-powered computer vision with agricultural mapping and analysis. Its primary purpose is to provide farmers and agricultural professionals with advanced, data-driven insights to improve agricultural productivity and decision-making. The platform enables users to analyze crops, detect diseases, count fruits, and visualize farm data through interactive maps and vegetation indices.

## User Preferences

Preferred communication style: Simple, everyday language.
**Critical Requirement**: 100% real AI data only - no mock, synthetic, or fallback data allowed.

## System Architecture

**Backend:**
- **Framework**: Flask with SQLAlchemy ORM.
- **Database**: SQLite (default), configurable to PostgreSQL.
- **Authentication**: Flask-Login for user session management.
- **AI Processing**: Integrated YOLO models for object detection and disease recognition, with robust error handling for missing models.
- **File Handling**: Local storage for uploads, with configurable limits and extensions.

**Frontend:**
- **Template Engine**: Jinja2, with robust client-side validation and secure rendering.
- **Styling**: Bootstrap with custom CSS, focusing on responsive design and consistent color schemes.
- **Interactive Maps**: Leaflet.js for GeoTIFF visualization, with enhanced error handling for tile layers.
- **Charts**: Chart.js for data visualization.
- **Language**: Turkish interface.
- **UI/UX Decisions**: Responsive design, professional layouts, enhanced navigation, and improved accessibility, including print-friendly styles and keyboard navigation.

**Core Features:**
- **User Management**: Registration, authentication, profile management, and password reset with strong validation.
- **Project Management**: Creation, tracking, and management of farm projects.
- **AI Detection**: YOLO-based fruit counting, disease identification, and multi-object detection using ensemble capabilities, with professional logging and error recovery.
- **Geospatial Analysis**: Processing of large agricultural imagery (GeoTIFF), calculation of vegetation indices (NDVI, EVI, SAVI), interactive mapping, and histogram analysis, with comprehensive data validation.
- **Data Storage**: Secure storage for user, project, and AI detection results.
- **Analytics Dashboard**: Professional analytics with authentic data visualization, including yield, confidence metrics, and activity trends.
- **Reporting System**: Generation of detailed reports for fruit detection and vegetation analysis, with filtering and multiple formats.

**System Design Choices:**
- Centralized configuration management using `python-dotenv` for environment-specific settings and security.
- Comprehensive security hardening across all components, including CSRF protection, input validation, and secure database interactions.
- Robust error handling and graceful degradation implemented across the system, especially for AI model loading and file operations.
- Type safety and professional logging standards across utility functions for improved maintainability and reliability.

## External Dependencies

- **Core Frameworks**: Flask, PyTorch, OpenCV, NumPy, SciPy.
- **Geospatial**: Rasterio, GDAL, Rio-tiler, Proj4.
- **Frontend Libraries**: Leaflet.js, Chart.js, Bootstrap, Font Awesome.
- **AI Models**: YOLO models (e.g., via Ultralytics) and custom-trained agricultural models.
- **Configuration**: `python-dotenv`.

## Recent Critical Updates

- **August 07, 2025**: Railway.app Production Deployment Configuration - Enterprise Cloud Deployment
  - **DEPLOYMENT READY**: Complete Railway.app deployment configuration with enterprise-grade production settings
  - **Railway.app Optimizations**:
    - nixpacks.toml: Configured with GDAL/PROJ system dependencies for geospatial processing
    - Procfile: Production Gunicorn configuration with optimized worker settings
    - railway.json: Railway-specific build and deployment settings
    - Enhanced ProductionConfig with Railway-specific database connection pooling
  - **Production Environment Detection**:
    - Automatic Railway environment detection in main.py startup
    - Force production settings when RAILWAY_ENVIRONMENT=production
    - Enhanced logging for Railway deployment monitoring
    - SSL-enforced database connections with increased connection limits
  - **Deployment Documentation**:
    - Complete DEPLOYMENT.md guide with step-by-step Railway deployment
    - Environment variables reference and security configuration
    - Production checklist and troubleshooting guide
    - Cost optimization and monitoring recommendations

- **August 07, 2025**: Production-Grade Main Application Files Audit - Enterprise-Level Configuration & Logging
  - **PRODUCTION CRITICAL**: Complete main application files hardening (main.py, config.py, app.py)
  - **Environment Variable Management Enhancement**:
    - config.py: Made python-dotenv mandatory in production environment with proper error handling
    - Enhanced production configuration validation with strict security checks
    - Implemented comprehensive configuration validation for missing required variables
    - Added production-specific database connection validation and SSL enforcement
  - **Application Startup Hardening**:
    - main.py: Completely redesigned with production-ready startup handling and comprehensive logging
    - Added environment-specific configuration with proper host/port handling
    - Implemented graceful shutdown handling and proper error reporting
    - Enhanced startup logging with detailed environment and configuration information
  - **Flask Application Security Enhancement**:
    - app.py: Enhanced directory creation with proper error handling and logging
    - Improved blueprint registration with comprehensive error handling
    - Added database table creation with proper error boundaries
    - Enhanced Flask-Login configuration with secure error handling
  - **Production Logging System**:
    - Replaced all print() statements with proper logger.info/debug/error calls
    - Implemented centralized logging configuration with file and console handlers
    - Added production-specific log level management and third-party logging suppression
    - Enhanced error tracking with detailed context and proper exception handling

- **August 07, 2025**: Production-Grade Static Assets Audit - Complete static/ Folder Enhancement
  - **PRODUCTION CRITICAL**: Comprehensive static file security and performance improvements across CSS and JavaScript
  - **JavaScript Production Hardening**:
    - mapping.js: Added robust tile layer error handling with fallback mechanisms and user-friendly error messages
    - Implemented comprehensive fetch timeout handling and network error recovery for API calls
    - Replaced all console.log() statements with production-ready error logging system
    - Enhanced map loading indicators and graceful degradation for failed tile layers
    - Added proper error boundaries for overlay loading with retry functionality
  - **CSS Mobile Responsiveness Enhancement**:
    - Completely redesigned responsive breakpoints with enhanced mobile support (991px, 768px, 576px)
    - Eliminated excessive !important usage while maintaining design integrity
    - Added comprehensive header positioning fixes for mobile devices
    - Implemented production-grade media queries with proper scaling and spacing
    - Enhanced navigation collapse behavior and dropdown positioning on mobile
  - **Performance & Accessibility Improvements**:
    - Added map loading indicators with spinner animations and progress feedback
    - Implemented print-friendly styles for better document export
    - Enhanced focus management and keyboard navigation support
    - Added proper error states for failed map tiles and API responses
  - **Production Error Logging System**:
    - Created centralized window.logError() function for consistent error tracking
    - Implemented silent error reporting to monitoring services in production
    - Enhanced user feedback with specific error messages and actionable guidance
    - All JavaScript files now have proper error boundaries and graceful degradation