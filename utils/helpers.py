import os
import uuid
import logging
import shutil
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, filename):
    """Fixed file saving with proper validation"""
    try:
        if not filename:
            raise ValueError("Filename cannot be empty")
            
        # Validate file extension
        if not allowed_file(filename):
            raise ValueError(f"File type not allowed: {get_file_extension(filename)}")
        
        # Generate secure filename
        secure_name = secure_filename(filename)
        if not secure_name:
            secure_name = f"upload_{uuid.uuid4().hex}.jpg"
            
        unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
        
        # Validate upload directory
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, mode=0o755)
            
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Check available disk space (at least 100MB)
        free_space = shutil.disk_usage(upload_dir).free
        if free_space < 100 * 1024 * 1024:  # 100MB
            raise OSError("Insufficient disk space")
        
        # Save file with size limit (10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("File too large (max 10MB)")
        
        file.save(file_path)
        
        # Verify file was saved correctly
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise OSError("File save failed")
            
        return file_path
        
    except Exception as e:
        logging.error(f"File save error: {e}")
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
