"""
Memory monitoring and management utilities for large file processing
"""

import os
import psutil
import gc
import logging
from functools import wraps
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MemoryMonitor:
    """Monitor and manage memory usage during processing"""
    
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.0
    
    def get_available_memory(self) -> float:
        """Get available system memory in MB"""
        try:
            memory = psutil.virtual_memory()
            return memory.available / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.error(f"Failed to get available memory: {e}")
            return 0.0
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage exceeds limit"""
        current_memory = self.get_memory_usage()
        return current_memory > self.max_memory_mb
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory"""
        try:
            gc.collect()
            logger.info("Forced garbage collection")
        except Exception as e:
            logger.error(f"Failed to force garbage collection: {e}")
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get comprehensive memory statistics"""
        try:
            current_memory = self.get_memory_usage()
            available_memory = self.get_available_memory()
            memory_increase = current_memory - self.initial_memory
            
            return {
                'current_mb': current_memory,
                'available_mb': available_memory,
                'increase_mb': memory_increase,
                'max_limit_mb': self.max_memory_mb,
                'usage_percent': (current_memory / self.max_memory_mb) * 100
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

def memory_monitor(max_memory_mb: int = 1024):
    """Decorator to monitor memory usage during function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = MemoryMonitor(max_memory_mb)
            
            try:
                # Log initial memory state
                initial_stats = monitor.get_memory_stats()
                logger.info(f"Starting {func.__name__} - Memory: {initial_stats.get('current_mb', 0):.1f}MB")
                
                # Check available memory before processing
                if initial_stats.get('available_mb', 0) < 200:  # Less than 200MB available
                    logger.warning("Low available memory, forcing garbage collection")
                    monitor.force_garbage_collection()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log final memory state
                final_stats = monitor.get_memory_stats()
                logger.info(f"Completed {func.__name__} - Memory: {final_stats.get('current_mb', 0):.1f}MB "
                           f"(+{final_stats.get('increase_mb', 0):.1f}MB)")
                
                # Check for memory leaks
                if final_stats.get('increase_mb', 0) > 100:  # More than 100MB increase
                    logger.warning(f"Potential memory leak detected in {func.__name__}")
                    monitor.force_garbage_collection()
                
                return result
                
            except MemoryError as e:
                logger.error(f"Memory error in {func.__name__}: {e}")
                monitor.force_garbage_collection()
                raise
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator

def check_file_size_limit(file_path: str, max_size_mb: int = 50) -> bool:
    """Check if file size is within acceptable limits"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size_mb = os.path.getsize(file_path) / 1024 / 1024
        
        if file_size_mb > max_size_mb:
            logger.warning(f"File {file_path} exceeds size limit: {file_size_mb:.1f}MB > {max_size_mb}MB")
            return False
        
        logger.info(f"File {file_path} size check passed: {file_size_mb:.1f}MB")
        return True
        
    except Exception as e:
        logger.error(f"Failed to check file size: {e}")
        return False

def estimate_processing_memory(file_path: str, processing_factor: float = 3.0) -> float:
    """Estimate memory required for processing a file"""
    try:
        file_size_mb = os.path.getsize(file_path) / 1024 / 1024
        estimated_memory_mb = file_size_mb * processing_factor
        
        logger.info(f"Estimated processing memory for {file_path}: {estimated_memory_mb:.1f}MB")
        return estimated_memory_mb
        
    except Exception as e:
        logger.error(f"Failed to estimate processing memory: {e}")
        return 0.0

def cleanup_temp_files(temp_dir: str = "/tmp", age_hours: int = 24):
    """Clean up temporary files older than specified age"""
    try:
        import time
        current_time = time.time()
        cutoff_time = current_time - (age_hours * 3600)
        
        cleaned_files = 0
        freed_space_mb = 0
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        file_size_mb = os.path.getsize(file_path) / 1024 / 1024
                        os.remove(file_path)
                        cleaned_files += 1
                        freed_space_mb += file_size_mb
                except Exception as e:
                    logger.warning(f"Could not clean temp file {file_path}: {e}")
        
        logger.info(f"Cleaned {cleaned_files} temp files, freed {freed_space_mb:.1f}MB")
        return cleaned_files, freed_space_mb
        
    except Exception as e:
        logger.error(f"Failed to cleanup temp files: {e}")
        return 0, 0.0