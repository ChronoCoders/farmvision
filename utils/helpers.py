import os
import uuid
import logging
import shutil
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'}

# MIME type whitelist for secure file validation
ALLOWED_MIME_TYPES = {
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/gif': ['.gif'],
    'image/tiff': ['.tif', '.tiff'],
    'application/octet-stream': ['.tif', '.tiff']  # Some GeoTIFFs report as octet-stream
}

# Magic number signatures for file type validation
FILE_SIGNATURES = {
    # Image format signatures
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'png',           # PNG
    b'\xFF\xD8\xFF': 'jpeg',                                # JPEG
    b'\x47\x49\x46\x38': 'gif',                            # GIF
    b'\x49\x49\x2A\x00': 'tiff',                           # TIFF (little-endian)
    b'\x4D\x4D\x00\x2A': 'tiff',                           # TIFF (big-endian)
    b'\x49\x49\x2B\x00': 'tiff',                           # BigTIFF (little-endian)
    b'\x4D\x4D\x00\x2B': 'tiff'                            # BigTIFF (big-endian)
}

def validate_file_security(file, filename):
    """
    Comprehensive file validation using multiple security layers:
    1. Extension validation
    2. MIME type checking  
    3. Magic number validation
    4. File size limits
    """
    from flask import current_app
    
    try:
        # Get allowed extensions from config
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'tif', 'tiff'})
        
        # Layer 1: Extension validation
        if not filename or not allowed_file_config(filename, allowed_extensions):
            return False, f"Desteklenmeyen dosya türü. İzin verilen: {', '.join(allowed_extensions)}"
        
        # Layer 2: MIME type validation
        mime_type = file.mimetype
        if mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Güvenlik uyarısı: MIME türü '{mime_type}' izin verilmiyor"
        
        # Verify extension matches MIME type
        file_ext = '.' + filename.rsplit('.', 1)[1].lower()
        if file_ext not in ALLOWED_MIME_TYPES.get(mime_type, []):
            return False, f"Dosya uzantısı ({file_ext}) MIME türü ({mime_type}) ile eşleşmiyor"
        
        # Layer 3: Magic number validation
        file.seek(0)
        header = file.read(8)  # Read first 8 bytes for magic number check
        file.seek(0)  # Reset file pointer
        
        detected_type = None
        for signature, file_type in FILE_SIGNATURES.items():
            if header.startswith(signature):
                detected_type = file_type
                break
        
        if not detected_type:
            return False, "Dosya imzası tanınamadı - potansiyel güvenlik riski"
        
        # Verify detected type matches extension
        expected_type = filename.rsplit('.', 1)[1].lower()
        if expected_type == 'jpg':
            expected_type = 'jpeg'  # Normalize jpg to jpeg
        
        if detected_type != expected_type:
            return False, f"Dosya içeriği ({detected_type}) uzantısı ({expected_type}) ile eşleşmiyor"
        
        # Layer 4: File size validation
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            return False, "Boş dosyalar yüklenemez"
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit for GeoTIFF
            return False, f"Dosya çok büyük (maksimum 50MB): {file_size / 1024 / 1024:.1f}MB"
        
        return True, "Dosya güvenlik kontrollerini geçti"
        
    except Exception as e:
        logging.error(f"File security validation error: {e}")
        return False, f"Dosya güvenlik kontrolü başarısız: {str(e)}"

def allowed_file(filename):
    """Check if file extension is allowed using global ALLOWED_EXTENSIONS"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_config(filename, allowed_extensions):
    """Check if file extension is allowed using provided extensions set"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, filename):
    """Enhanced secure file saving with comprehensive validation"""
    try:
        if not filename:
            raise ValueError("Dosya adı boş olamaz")
        
        # Comprehensive security validation
        is_valid, error_msg = validate_file_security(file, filename)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Generate secure filename
        secure_name = secure_filename(filename)
        if not secure_name:
            ext = get_file_extension(filename)
            secure_name = f"upload_{uuid.uuid4().hex}.{ext}"
            
        unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
        
        # Validate upload directory
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, mode=0o755)
            
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Check available disk space (at least 200MB for GeoTIFF processing)
        free_space = shutil.disk_usage(upload_dir).free
        if free_space < 200 * 1024 * 1024:  # 200MB
            raise OSError("Yetersiz disk alanı (en az 200MB gerekli)")
        
        # Save file securely
        file.seek(0)  # Reset to beginning before save
        file.save(file_path)
        
        # Verify file was saved correctly
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise OSError("Dosya kaydetme başarısız")
        
        # Final security check: Re-validate saved file
        try:
            with open(file_path, 'rb') as saved_file:
                header = saved_file.read(8)
                detected_type = None
                for signature, file_type in FILE_SIGNATURES.items():
                    if header.startswith(signature):
                        detected_type = file_type
                        break
                
                if not detected_type:
                    os.remove(file_path)  # Remove suspicious file
                    raise ValueError("Kaydedilen dosya güvenlik kontrolünü geçemedi")
                    
        except Exception as verify_error:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Dosya doğrulama hatası: {verify_error}")
            
        logging.info(f"File saved securely: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Secure file save error: {e}")
        raise

def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def generate_hash():
    """Generate a random hash for file naming"""
    return uuid.uuid4().hex[:16]
