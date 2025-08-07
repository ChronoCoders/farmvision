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

## Recent Critical Updates

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