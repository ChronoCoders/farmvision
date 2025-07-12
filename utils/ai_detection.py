import os
import cv2
import torch
import numpy as np
import logging
from pathlib import Path
from PIL import Image
from typing import Dict, Any, Optional

from utils.memory_monitor import memory_monitor, MemoryMonitor
from utils.input_validation import InputValidator
from utils.timeout_control import timeout_decorator, ProcessTimer, TIMEOUT_CONFIGS

logger = logging.getLogger(__name__)

class AIDetectionError(Exception):
    """Custom exception for AI detection errors"""
    pass

class SafeAIDetector:
    """Thread-safe AI detector with comprehensive error handling"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.memory_monitor = MemoryMonitor(max_memory_mb)
        self.validator = InputValidator()
        
    def _validate_model_file(self, model_path: str) -> bool:
        """Validate model file exists and is accessible"""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Check file size (models should be 70-300MB)
            file_size_mb = os.path.getsize(model_path) / 1024 / 1024
            if file_size_mb < 70 or file_size_mb > 300:
                raise ValueError(f"Invalid model file size: {file_size_mb:.1f}MB. Expected 70-300MB")
            
            # Check file extension
            if not model_path.endswith(('.pt', '.pth', '.onnx')):
                raise ValueError(f"Invalid model file extension: {model_path}")
            
            logger.info(f"Model validation passed: {model_path} ({file_size_mb:.1f}MB)")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            raise AIDetectionError(f"Model validation failed: {e}")
    
    def _validate_input_image(self, image_path: str) -> Dict[str, Any]:
        """Validate input image file"""
        validation_result = self.validator.validate_file_upload(image_path, 'image')
        
        if not validation_result['valid']:
            error_msg = f"Image validation failed: {'; '.join(validation_result['errors'])}"
            logger.error(error_msg)
            raise AIDetectionError(error_msg)
        
        return validation_result['file_info']
    
    def _preprocess_image_safely(self, image_path: str) -> Optional[np.ndarray]:
        """Safely preprocess image with memory monitoring"""
        try:
            # Check memory before loading
            if self.memory_monitor.check_memory_limit():
                self.memory_monitor.force_garbage_collection()
                
            # Load image with error handling
            image = cv2.imread(image_path)
            if image is None:
                # Try with PIL as fallback
                try:
                    pil_image = Image.open(image_path)
                    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                except Exception as e:
                    raise AIDetectionError(f"Could not load image: {e}")
            
            # Validate image dimensions
            if len(image.shape) != 3 or image.shape[2] != 3:
                raise AIDetectionError("Invalid image format - expected 3-channel RGB image")
            
            h, w = image.shape[:2]
            if h == 0 or w == 0:
                raise AIDetectionError("Invalid image dimensions")
            
            # Resize if too large to prevent memory issues
            max_dimension = 2048
            if max(h, w) > max_dimension:
                scale = max_dimension / max(h, w)
                new_h, new_w = int(h * scale), int(w * scale)
                image = cv2.resize(image, (new_w, new_h))
                logger.info(f"Resized image from {w}x{h} to {new_w}x{new_h}")
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise AIDetectionError(f"Image preprocessing failed: {e}")
    
    def _cleanup_temp_files(self, temp_files: list):
        """Clean up temporary files"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Could not clean up temp file {temp_file}: {e}")

@timeout_decorator(TIMEOUT_CONFIGS['ai_inference'])
@memory_monitor(max_memory_mb=2048)
def detect_fruits(image_path: str, fruit_type: str = 'elma') -> Dict[str, Any]:
    """
    Detect fruits in the given image using YOLO model - AUTHENTIC AI ONLY
    Enhanced with comprehensive error handling and validation
    """
    detector = SafeAIDetector()
    timer = ProcessTimer(f"Fruit Detection ({fruit_type})", TIMEOUT_CONFIGS['ai_inference'])
    temp_files = []
    
    try:
        timer.start()
        
        # Validate inputs
        if not fruit_type or fruit_type not in ['elma', 'armut', 'portakal', 'mandalina', 'seftali', 'nar', 'limon', 'hurma']:
            raise AIDetectionError(f"Invalid fruit type: {fruit_type}")
        
        # Validate image file
        image_info = detector._validate_input_image(image_path)
        logger.info(f"Processing image: {image_path} ({image_info['size_mb']:.1f}MB)")
        
        # Validate model file
        model_path = f"detection_models/{fruit_type}_detection.pt"
        detector._validate_model_file(model_path)
        
        # Preprocess image
        processed_image = detector._preprocess_image_safely(image_path)
        if processed_image is None:
            raise AIDetectionError("Image preprocessing failed")
        
        # Check memory usage
        memory_stats = detector.memory_monitor.get_memory_stats()
        if memory_stats.get('usage_percent', 0) > 80:
            logger.warning(f"High memory usage: {memory_stats['usage_percent']:.1f}%")
        
        # Real YOLO inference would go here
        # For now, return error since we don't have real models
        raise NotImplementedError("Real YOLO models not available. Please provide authentic model files (70-300MB .pt files)")
        
    except TimeoutError as e:
        logger.error(f"Fruit detection timed out: {e}")
        return {
            'success': False,
            'error': f'Detection timed out after {TIMEOUT_CONFIGS["ai_inference"]} seconds',
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except AIDetectionError as e:
        logger.error(f"AI detection error: {e}")
        return {
            'success': False,
            'error': str(e),
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except Exception as e:
        logger.error(f"Unexpected error in fruit detection: {e}")
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    finally:
        timer.stop()
        detector._cleanup_temp_files(temp_files)

@timeout_decorator(TIMEOUT_CONFIGS['ai_inference'])
@memory_monitor(max_memory_mb=2048)
def detect_leaf_disease(image_path: str) -> Dict[str, Any]:
    """
    Detect leaf diseases using YOLO model - AUTHENTIC AI ONLY
    Enhanced with comprehensive error handling and validation
    """
    detector = SafeAIDetector()
    timer = ProcessTimer("Leaf Disease Detection", TIMEOUT_CONFIGS['ai_inference'])
    temp_files = []
    
    try:
        timer.start()
        
        # Validate image file
        image_info = detector._validate_input_image(image_path)
        logger.info(f"Processing image: {image_path} ({image_info['size_mb']:.1f}MB)")
        
        # Validate model file
        model_path = "detection_models/leaf_disease_detection.pt"
        detector._validate_model_file(model_path)
        
        # Preprocess image
        processed_image = detector._preprocess_image_safely(image_path)
        if processed_image is None:
            raise AIDetectionError("Image preprocessing failed")
        
        # Real YOLO inference would go here
        raise NotImplementedError("Real YOLO models not available. Please provide authentic model files (70-300MB .pt files)")
        
    except TimeoutError as e:
        logger.error(f"Leaf disease detection timed out: {e}")
        return {
            'success': False,
            'error': f'Detection timed out after {TIMEOUT_CONFIGS["ai_inference"]} seconds',
            'disease_type': None,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except AIDetectionError as e:
        logger.error(f"AI detection error: {e}")
        return {
            'success': False,
            'error': str(e),
            'disease_type': None,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except Exception as e:
        logger.error(f"Unexpected error in leaf disease detection: {e}")
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'disease_type': None,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    finally:
        timer.stop()
        detector._cleanup_temp_files(temp_files)

@timeout_decorator(TIMEOUT_CONFIGS['ai_inference'])
@memory_monitor(max_memory_mb=2048)
def detect_trees(image_path: str) -> Dict[str, Any]:
    """
    Detect trees in the given image using YOLO model - AUTHENTIC AI ONLY
    Enhanced with comprehensive error handling and validation
    """
    detector = SafeAIDetector()
    timer = ProcessTimer("Tree Detection", TIMEOUT_CONFIGS['ai_inference'])
    temp_files = []
    
    try:
        timer.start()
        
        # Validate image file
        image_info = detector._validate_input_image(image_path)
        logger.info(f"Processing image: {image_path} ({image_info['size_mb']:.1f}MB)")
        
        # Validate model file
        model_path = "detection_models/tree_detection.pt"
        detector._validate_model_file(model_path)
        
        # Preprocess image
        processed_image = detector._preprocess_image_safely(image_path)
        if processed_image is None:
            raise AIDetectionError("Image preprocessing failed")
        
        # Real YOLO inference would go here
        raise NotImplementedError("Real YOLO models not available. Please provide authentic model files (70-300MB .pt files)")
        
    except TimeoutError as e:
        logger.error(f"Tree detection timed out: {e}")
        return {
            'success': False,
            'error': f'Detection timed out after {TIMEOUT_CONFIGS["ai_inference"]} seconds',
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except AIDetectionError as e:
        logger.error(f"AI detection error: {e}")
        return {
            'success': False,
            'error': str(e),
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    except Exception as e:
        logger.error(f"Unexpected error in tree detection: {e}")
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'count': 0,
            'confidence': 0.0,
            'result_path': None,
            'processing_time': timer.get_elapsed()
        }
    finally:
        timer.stop()
        detector._cleanup_temp_files(temp_files)
