import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import uuid

def resize_image(image_path, max_size=(1024, 1024), maintain_aspect=True):
    """
    Resize image while maintaining aspect ratio
    """
    try:
        with Image.open(image_path) as img:
            if maintain_aspect:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(max_size, Image.Resampling.LANCZOS)
            
            # Save resized image
            resized_path = f"static/processed/resized_{uuid.uuid4().hex}.jpg"
            os.makedirs(os.path.dirname(resized_path), exist_ok=True)
            
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(resized_path, "JPEG", quality=90)
            return resized_path
            
    except Exception as e:
        raise Exception(f"Görüntü boyutlandırma hatası: {str(e)}")

def enhance_image(image_path, brightness=1.0, contrast=1.0, saturation=1.0):
    """
    Enhance image properties
    """
    try:
        with Image.open(image_path) as img:
            # Brightness enhancement
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            # Contrast enhancement
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            
            # Color saturation enhancement
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)
            
            # Save enhanced image
            enhanced_path = f"static/processed/enhanced_{uuid.uuid4().hex}.jpg"
            os.makedirs(os.path.dirname(enhanced_path), exist_ok=True)
            
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(enhanced_path, "JPEG", quality=95)
            return enhanced_path
            
    except Exception as e:
        raise Exception(f"Görüntü iyileştirme hatası: {str(e)}")

def convert_tiff_to_jpg(tiff_path, output_path=None):
    """
    Convert TIFF to JPEG format
    """
    try:
        with Image.open(tiff_path) as img:
            if output_path is None:
                output_path = f"static/converted/converted_{uuid.uuid4().hex}.jpg"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert to RGB mode
            if img.mode in ("RGBA", "P", "L"):
                img = img.convert("RGB")
            
            img.save(output_path, "JPEG", quality=90)
            return output_path
            
    except Exception as e:
        raise Exception(f"TIFF dönüştürme hatası: {str(e)}")

def create_thumbnail(image_path, size=(200, 200)):
    """
    Create thumbnail of image
    """
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            thumbnail_path = f"static/thumbnails/thumb_{uuid.uuid4().hex}.jpg"
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(thumbnail_path, "JPEG", quality=85)
            return thumbnail_path
            
    except Exception as e:
        raise Exception(f"Küçük resim oluşturma hatası: {str(e)}")

def apply_filters(image_path, filter_type="none"):
    """
    Apply various filters to image
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Görüntü yüklenemedi")
        
        if filter_type == "blur":
            filtered = cv2.GaussianBlur(image, (15, 15), 0)
        elif filter_type == "sharpen":
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            filtered = cv2.filter2D(image, -1, kernel)
        elif filter_type == "edge":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            filtered = cv2.Canny(gray, 50, 150)
            filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        elif filter_type == "emboss":
            kernel = np.array([[-2,-1,0], [-1,1,1], [0,1,2]])
            filtered = cv2.filter2D(image, -1, kernel)
        else:
            filtered = image
        
        # Save filtered image
        filtered_path = f"static/processed/filtered_{uuid.uuid4().hex}.jpg"
        os.makedirs(os.path.dirname(filtered_path), exist_ok=True)
        cv2.imwrite(filtered_path, filtered)
        
        return filtered_path
        
    except Exception as e:
        raise Exception(f"Filtre uygulama hatası: {str(e)}")

def get_image_info(image_path):
    """
    Get image information
    """
    try:
        with Image.open(image_path) as img:
            info = {
                'filename': os.path.basename(image_path),
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': os.path.getsize(image_path)
            }
            
            # Add EXIF data if available
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                info['exif'] = exif
            
            return info
            
    except Exception as e:
        raise Exception(f"Görüntü bilgisi alma hatası: {str(e)}")

def batch_process_images(image_paths, operations):
    """
    Process multiple images with given operations
    """
    results = []
    
    for image_path in image_paths:
        try:
            processed_path = image_path
            
            for operation in operations:
                if operation['type'] == 'resize':
                    processed_path = resize_image(processed_path, 
                                                operation.get('size', (1024, 1024)))
                elif operation['type'] == 'enhance':
                    processed_path = enhance_image(processed_path,
                                                 operation.get('brightness', 1.0),
                                                 operation.get('contrast', 1.0),
                                                 operation.get('saturation', 1.0))
                elif operation['type'] == 'filter':
                    processed_path = apply_filters(processed_path,
                                                 operation.get('filter_type', 'none'))
            
            results.append({
                'original': image_path,
                'processed': processed_path,
                'status': 'success'
            })
            
        except Exception as e:
            results.append({
                'original': image_path,
                'processed': None,
                'status': 'error',
                'error': str(e)
            })
    
    return results
