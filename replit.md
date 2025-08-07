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