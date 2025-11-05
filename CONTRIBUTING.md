# Contributing to FarmVision

First off, thank you for considering contributing to FarmVision! It's people like you that make FarmVision such a great tool for agricultural intelligence.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

#### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g., Windows 10, Ubuntu 22.04]
 - Python Version: [e.g., 3.10.5]
 - Django Version: [e.g., 4.2.17]
 - Browser: [e.g., Chrome 120, Firefox 115]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Explain why this enhancement would be useful
- List any additional resources or references

#### Enhancement Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Pull Requests

#### Development Process

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/farmvision.git
   cd farmvision
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If exists
   ```

4. **Make Your Changes**
   - Write clean, readable code
   - Follow the project's coding standards
   - Add or update tests as needed
   - Update documentation if required

5. **Run Tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=. --cov-report=html

   # Run specific test file
   pytest detection/tests/test_views.py
   ```

6. **Run Linters and Formatters**
   ```bash
   # Format code with black
   black .

   # Check with flake8
   flake8 .

   # Type checking with mypy
   mypy .

   # Security check
   bandit -r .
   ```

7. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

   **Commit Message Guidelines:**
   - Use the present tense ("Add feature" not "Added feature")
   - Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
   - Limit the first line to 72 characters or less
   - Reference issues and pull requests liberally after the first line

   **Examples:**
   ```
   Add YOLOv8 model caching for faster inference

   Fix dropdown menu positioning in projects list

   Update documentation for Docker deployment

   Refactor image processing pipeline for better performance
   ```

8. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

#### Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**:
  - What changes were made?
  - Why were these changes necessary?
  - How have the changes been tested?
  - Any breaking changes?
- **Link Issues**: Reference related issues (e.g., "Fixes #123")
- **Screenshots**: Include before/after screenshots for UI changes
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation

#### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## How Has This Been Tested?
Describe the tests that you ran to verify your changes.

- [ ] Test A
- [ ] Test B

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
Add screenshots to demonstrate the changes.
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Imports**:
  - Standard library imports
  - Related third party imports
  - Local application imports
  - Separated by blank lines

```python
# Standard library
import os
import sys
from pathlib import Path

# Third party
from django.db import models
from rest_framework import serializers

# Local
from detection.models import Detection
from dron_map.utils import process_image
```

### Django Best Practices

- Use class-based views when appropriate
- Keep views thin, models fat
- Use Django ORM instead of raw SQL
- Write meaningful docstrings
- Use Django's built-in authentication
- Follow Django's naming conventions

### Testing Standards

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest fixtures for setup
- Mock external dependencies
- Test both success and failure cases

```python
import pytest
from django.test import TestCase

class TestProjectCreation(TestCase):
    """Test suite for project creation functionality."""

    def test_create_project_success(self):
        """Test successful project creation."""
        # Arrange
        data = {...}

        # Act
        response = self.client.post('/projects/add/', data)

        # Assert
        self.assertEqual(response.status_code, 302)
```

### Documentation Standards

- Write clear, concise docstrings
- Use Google style docstrings
- Document all public APIs
- Include examples where helpful

```python
def process_drone_image(image_path: str, model_name: str = "yolov8n") -> Dict[str, Any]:
    """
    Process a drone image using the specified YOLO model.

    Args:
        image_path: Path to the image file to process.
        model_name: Name of the YOLO model to use. Defaults to "yolov8n".

    Returns:
        Dictionary containing detection results with bounding boxes and confidence scores.

    Raises:
        FileNotFoundError: If image_path does not exist.
        ValueError: If model_name is not supported.

    Example:
        >>> results = process_drone_image("field.jpg", "yolov8m")
        >>> print(results['detections'])
    """
    pass
```

## Development Environment Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 13+ with PostGIS
- Redis 6+
- GDAL 3.8+

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/farmvision.git
cd farmvision

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific app
pytest detection/

# Specific test
pytest detection/tests/test_views.py::TestProjectViews::test_create_project
```

### Code Quality Tools

```bash
# Format code
black .

# Lint
flake8 .
ruff check .

# Type checking
mypy .

# Security
bandit -r .

# All checks at once
pre-commit run --all-files
```

## Project Structure

```
farmvision/
├── detection/              # Detection app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   └── tests/             # Test files
├── dron_map/              # Drone project management
├── yolowebapp2/           # Main project settings
├── templates/             # HTML templates
├── static/                # Static files
└── tests/                 # Integration tests
```

## Getting Help

- **Documentation**: Check the [README.md](README.md) and [Wiki](https://github.com/yourusername/farmvision/wiki)
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainers at support@farmvision.com

## Recognition

Contributors will be recognized in:
- The project's README.md
- Release notes
- Hall of fame (for significant contributions)

## License

By contributing to FarmVision, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FarmVision!
