"""
Timeout control utilities for long-running operations
"""

import signal
import time
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Operation timed out")

@contextmanager
def timeout_context(seconds: int):
    """Context manager for timeout control"""
    # Set up signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    
    try:
        signal.alarm(seconds)
        yield
    except TimeoutError:
        logger.error(f"Operation timed out after {seconds} seconds")
        raise
    finally:
        signal.alarm(0)  # Cancel alarm
        signal.signal(signal.SIGALRM, old_handler)  # Restore old handler

def timeout_decorator(seconds: int, error_message: Optional[str] = None):
    """Decorator to add timeout to function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_msg = error_message or f"{func.__name__} operation timed out after {seconds} seconds"
            
            try:
                with timeout_context(seconds):
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
                    return result
                    
            except TimeoutError:
                logger.error(error_msg)
                raise TimeoutError(error_msg)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator

class ProcessTimer:
    """Timer for monitoring process execution"""
    
    def __init__(self, name: str, timeout_seconds: int = 300):
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.end_time = None
        
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        logger.info(f"Starting {self.name} - timeout: {self.timeout_seconds}s")
        
    def check_timeout(self):
        """Check if operation has timed out"""
        if self.start_time is None:
            return False
            
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            logger.error(f"{self.name} timed out after {elapsed:.2f}s")
            raise TimeoutError(f"{self.name} timed out after {elapsed:.2f}s")
        
        return False
        
    def stop(self):
        """Stop the timer and log completion"""
        if self.start_time is None:
            logger.warning(f"{self.name} timer was never started")
            return 0
            
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        logger.info(f"{self.name} completed in {elapsed:.2f}s")
        
        return elapsed
    
    def get_elapsed(self) -> float:
        """Get elapsed time without stopping"""
        if self.start_time is None:
            return 0
        
        return time.time() - self.start_time

# Timeout configurations for different operations
TIMEOUT_CONFIGS = {
    'image_upload': 30,      # 30 seconds
    'image_processing': 120,  # 2 minutes
    'ai_inference': 180,     # 3 minutes
    'geotiff_processing': 300, # 5 minutes
    'vegetation_analysis': 240, # 4 minutes
    'batch_processing': 600,  # 10 minutes
    'database_operation': 30, # 30 seconds
    'file_cleanup': 60,      # 1 minute
}

def get_timeout_for_operation(operation_type: str) -> int:
    """Get timeout duration for specific operation type"""
    return TIMEOUT_CONFIGS.get(operation_type, 300)  # Default 5 minutes

@timeout_decorator(TIMEOUT_CONFIGS['image_processing'])
def safe_image_processing(func: Callable, *args, **kwargs):
    """Safe wrapper for image processing operations"""
    return func(*args, **kwargs)

@timeout_decorator(TIMEOUT_CONFIGS['ai_inference'])
def safe_ai_inference(func: Callable, *args, **kwargs):
    """Safe wrapper for AI inference operations"""
    return func(*args, **kwargs)

@timeout_decorator(TIMEOUT_CONFIGS['geotiff_processing'])
def safe_geotiff_processing(func: Callable, *args, **kwargs):
    """Safe wrapper for GeoTIFF processing operations"""
    return func(*args, **kwargs)

class BatchProcessingTimer:
    """Timer for batch processing operations with progress tracking"""
    
    def __init__(self, total_items: int, timeout_per_item: int = 30):
        self.total_items = total_items
        self.timeout_per_item = timeout_per_item
        self.processed_items = 0
        self.start_time = None
        self.failed_items = []
        
    def start(self):
        """Start batch processing timer"""
        self.start_time = time.time()
        total_timeout = self.total_items * self.timeout_per_item
        logger.info(f"Starting batch processing of {self.total_items} items - "
                   f"timeout per item: {self.timeout_per_item}s, total timeout: {total_timeout}s")
        
    def process_item(self, item_id: Any, func: Callable, *args, **kwargs):
        """Process a single item with timeout control"""
        if self.start_time is None:
            self.start()
            
        item_timer = ProcessTimer(f"Item {item_id}", self.timeout_per_item)
        
        try:
            item_timer.start()
            result = func(*args, **kwargs)
            item_timer.stop()
            
            self.processed_items += 1
            progress = (self.processed_items / self.total_items) * 100
            logger.info(f"Processed item {item_id} - Progress: {progress:.1f}%")
            
            return result
            
        except TimeoutError as e:
            self.failed_items.append(item_id)
            logger.error(f"Item {item_id} timed out: {e}")
            raise
        except Exception as e:
            self.failed_items.append(item_id)
            logger.error(f"Item {item_id} failed: {e}")
            raise
            
    def get_summary(self) -> dict:
        """Get processing summary"""
        if self.start_time is None:
            return {"status": "not_started"}
            
        elapsed = time.time() - self.start_time
        
        return {
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": len(self.failed_items),
            "failed_item_ids": self.failed_items,
            "elapsed_seconds": elapsed,
            "success_rate": (self.processed_items / self.total_items) * 100 if self.total_items > 0 else 0
        }