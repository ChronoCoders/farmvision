"""
Input validation utilities for user-supplied parameters
"""

import re
import os
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """Comprehensive input validation utility"""
    
    # File extension whitelist
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif'}
    ALLOWED_GEOTIFF_EXTENSIONS = {'.tif', '.tiff', '.geotiff'}
    
    # Size limits (in bytes)
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_GEOTIFF_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,15}$')
    
    @staticmethod
    def validate_file_upload(file_path: str, file_type: str = 'image') -> Dict[str, Any]:
        """Validate uploaded file comprehensively"""
        validation_result = {
            'valid': False,
            'errors': [],
            'file_info': {}
        }
        
        try:
            # Check file existence
            if not os.path.exists(file_path):
                validation_result['errors'].append(f"File not found: {file_path}")
                return validation_result
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            validation_result['file_info'] = {
                'size_bytes': file_size,
                'size_mb': file_size / 1024 / 1024,
                'extension': file_ext,
                'path': file_path
            }
            
            # Validate file extension
            if file_type == 'image':
                if file_ext not in InputValidator.ALLOWED_IMAGE_EXTENSIONS:
                    validation_result['errors'].append(f"Invalid image extension: {file_ext}")
                max_size = InputValidator.MAX_IMAGE_SIZE
            elif file_type == 'geotiff':
                if file_ext not in InputValidator.ALLOWED_GEOTIFF_EXTENSIONS:
                    validation_result['errors'].append(f"Invalid GeoTIFF extension: {file_ext}")
                max_size = InputValidator.MAX_GEOTIFF_SIZE
            else:
                validation_result['errors'].append(f"Unknown file type: {file_type}")
                return validation_result
            
            # Validate file size
            if file_size > max_size:
                validation_result['errors'].append(
                    f"File too large: {file_size / 1024 / 1024:.1f}MB > {max_size / 1024 / 1024:.1f}MB"
                )
            
            # Check if file is empty
            if file_size == 0:
                validation_result['errors'].append("File is empty")
            
            # Validate file is readable
            try:
                with open(file_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB to check readability
            except Exception as e:
                validation_result['errors'].append(f"File not readable: {e}")
            
            # If no errors, file is valid
            if not validation_result['errors']:
                validation_result['valid'] = True
                logger.info(f"File validation passed: {file_path}")
            else:
                logger.warning(f"File validation failed: {file_path} - {validation_result['errors']}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            validation_result['errors'].append(f"Validation error: {e}")
            return validation_result
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username or not isinstance(username, str):
            return False
        
        username = username.strip()
        return bool(InputValidator.USERNAME_PATTERN.match(username))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        phone = phone.strip()
        return bool(InputValidator.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: float, max_val: float, 
                              field_name: str = "value") -> float:
        """Validate numeric value within specified range"""
        try:
            num_value = float(value)
            
            if num_value < min_val or num_value > max_val:
                raise ValidationError(
                    f"{field_name} must be between {min_val} and {max_val}, got {num_value}"
                )
            
            return num_value
            
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number, got {value}")
    
    @staticmethod
    def validate_string_length(value: str, min_len: int, max_len: int, 
                              field_name: str = "value") -> str:
        """Validate string length"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string, got {type(value)}")
        
        value = value.strip()
        
        if len(value) < min_len or len(value) > max_len:
            raise ValidationError(
                f"{field_name} length must be between {min_len} and {max_len}, got {len(value)}"
            )
        
        return value
    
    @staticmethod
    def validate_choice(value: Any, choices: List[Any], field_name: str = "value") -> Any:
        """Validate value is in allowed choices"""
        if value not in choices:
            raise ValidationError(f"{field_name} must be one of {choices}, got {value}")
        
        return value
    
    @staticmethod
    def validate_vegetation_params(algorithm: str, ranges: tuple, colormap: str) -> Dict[str, Any]:
        """Validate vegetation analysis parameters"""
        validation_result = {
            'valid': False,
            'errors': [],
            'validated_params': {}
        }
        
        try:
            # Validate algorithm
            allowed_algorithms = [
                'ndvi', 'gli', 'vari', 'ndyi', 'ndre', 'ndwi', 'ndvi_blue',
                'endvi', 'vndvi', 'mpri', 'exg', 'tgi', 'bai', 'gndvi', 'savi'
            ]
            algorithm = InputValidator.validate_choice(algorithm, allowed_algorithms, "algorithm")
            
            # Validate ranges
            if not isinstance(ranges, (tuple, list)) or len(ranges) != 2:
                raise ValidationError("Ranges must be a tuple/list of 2 values")
            
            min_range = InputValidator.validate_numeric_range(ranges[0], -10, 10, "min_range")
            max_range = InputValidator.validate_numeric_range(ranges[1], -10, 10, "max_range")
            
            if min_range >= max_range:
                raise ValidationError("min_range must be less than max_range")
            
            # Validate colormap
            allowed_colormaps = ['rdylgn', 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm']
            colormap = InputValidator.validate_choice(colormap, allowed_colormaps, "colormap")
            
            validation_result['validated_params'] = {
                'algorithm': algorithm,
                'ranges': (min_range, max_range),
                'colormap': colormap
            }
            validation_result['valid'] = True
            
        except ValidationError as e:
            validation_result['errors'].append(str(e))
            logger.error(f"Vegetation parameter validation failed: {e}")
        except Exception as e:
            validation_result['errors'].append(f"Unexpected validation error: {e}")
            logger.error(f"Unexpected validation error: {e}")
        
        return validation_result
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            return "unnamed_file"
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        # Ensure filename is not empty after sanitization
        if not filename or filename == '.':
            filename = "unnamed_file"
        
        return filename
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> tuple:
        """Validate geographic coordinates"""
        try:
            lat = InputValidator.validate_numeric_range(lat, -90, 90, "latitude")
            lon = InputValidator.validate_numeric_range(lon, -180, 180, "longitude")
            return lat, lon
        except ValidationError:
            raise
    
    @staticmethod
    def validate_project_params(title: str, description: str, farm_name: str, 
                               location: str) -> Dict[str, str]:
        """Validate project creation parameters"""
        validated_params = {}
        
        # Validate title
        validated_params['title'] = InputValidator.validate_string_length(
            title, 3, 200, "title"
        )
        
        # Validate description (optional)
        if description:
            validated_params['description'] = InputValidator.validate_string_length(
                description, 0, 1000, "description"
            )
        else:
            validated_params['description'] = ""
        
        # Validate farm name
        validated_params['farm_name'] = InputValidator.validate_string_length(
            farm_name, 2, 100, "farm_name"
        )
        
        # Validate location
        validated_params['location'] = InputValidator.validate_string_length(
            location, 2, 200, "location"
        )
        
        return validated_params