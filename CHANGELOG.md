# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup with Django 4.2.17
- YOLOv8 integration for object detection
- Drone project management system
- WebODM integration for orthophoto processing
- System monitoring dashboard
- RESTful API with DRF
- Turkish language support
- User authentication and authorization
- Redis caching layer
- Celery task queue integration
- PostgreSQL database support

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed dropdown menu positioning in drone projects list
- Fixed form visibility issue on add projects page - added missing `userss` context variable

### Security
- Added CSRF protection
- Implemented Content Security Policy (CSP)
- Added input validation for file uploads
- Implemented path traversal prevention
- Added SQL injection protection via Django ORM

## [1.0.0] - 2025-01-XX

### Added

#### Core Features
- **Drone Project Management**
  - Create, read, update, delete (CRUD) operations for drone projects
  - Project fields: Farm, Field, Title, Status, Images, Timestamp
  - Image upload with validation (JPEG, PNG, TIFF formats, max 10MB)
  - Automatic project directory creation with hashing

- **AI-Powered Detection**
  - YOLOv8 model integration for object detection
  - Multi-image batch processing
  - Support for multiple model sizes (nano to extra-large)
  - Real-time detection with bounding boxes
  - Confidence score filtering

- **Orthophoto Processing**
  - Drone image stitching
  - Georeferencing support
  - WebODM integration for advanced processing
  - GeoTIFF output generation

- **System Monitoring**
  - Real-time CPU usage tracking
  - GPU utilization monitoring (CUDA support)
  - Memory usage statistics
  - Disk I/O metrics
  - Network statistics
  - Loaded ML models tracking
  - Process monitoring

- **Interactive Mapping**
  - Map view for drone projects
  - Orthophoto overlay
  - Detection results visualization
  - GIS integration with GDAL

#### API Features
- RESTful API with Django REST Framework
- Token-based authentication
- API documentation with Swagger/ReDoc
- Filtering, searching, and pagination support
- Rate limiting and throttling

#### UI/UX
- Responsive Bootstrap-based interface
- Turkish language support throughout
- Interactive dashboards
- Real-time status updates
- File upload with preview
- Error handling with user-friendly messages

#### Infrastructure
- Django 4.2.17 framework
- PostgreSQL database with PostGIS
- Redis for caching and session management
- Celery for asynchronous task processing
- Gunicorn WSGI server
- Docker containerization support

#### Security
- User authentication and authorization
- Django Guardian for object-level permissions
- CSRF protection
- Content Security Policy (CSP)
- Secure file upload handling
- Path traversal prevention
- Input validation and sanitization

#### Developer Tools
- Comprehensive test suite with pytest
- Code coverage reporting
- Type hints and mypy support
- Linting with flake8 and ruff
- Code formatting with black
- Pre-commit hooks
- Security scanning with bandit

### Changed
- N/A (Initial release)

### Fixed
- Initial bug fixes and stability improvements

### Security
- Implemented comprehensive security measures for initial release

## Version History

### [1.0.0] - Initial Release
- First stable release of FarmVision
- Complete drone project management system
- YOLOv8 integration
- WebODM support
- System monitoring
- RESTful API

---

## How to Update This Changelog

When making changes:

1. Add entries under the "Unreleased" section
2. Categorize changes as: Added, Changed, Deprecated, Removed, Fixed, Security
3. When releasing a new version:
   - Move unreleased items to a new version section
   - Add the release date
   - Create a new empty "Unreleased" section

Example entry format:
```markdown
### Added
- Feature description with details
- Another feature with relevant information

### Fixed
- Bug fix description with issue reference if applicable
```

---

## Links

- [Repository](https://github.com/ChronoCoders/farmvision)
- [Issue Tracker](https://github.com/ChronoCoders/farmvision/issues)
- [Documentation](https://github.com/ChronoCoders/farmvision/wiki)
