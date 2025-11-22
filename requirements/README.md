# Requirements

This directory contains split requirements files for different environments.

## Files

- **base.txt** - Core dependencies required for all environments
- **dev.txt** - Development tools (testing, linting, type checking)
- **prod.txt** - Production-specific packages (monitoring, PostgreSQL)

## Usage

### Development
```bash
pip install -r requirements/dev.txt
```

### Production
```bash
pip install -r requirements/prod.txt
```

### Base Only
```bash
pip install -r requirements/base.txt
```

## Migration from requirements.txt

The original `requirements.txt` has been split for better dependency management.
To update the old format:
```bash
pip freeze > requirements-freeze.txt
```

## Adding New Dependencies

- Add to **base.txt** if needed in all environments
- Add to **dev.txt** if only needed for development
- Add to **prod.txt** if only needed in production
