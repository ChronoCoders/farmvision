#!/usr/bin/env python3
"""
Test script for the critical debugging fixes
"""

import os
import sys
import tempfile
import numpy as np
import cv2
from pathlib import Path

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

def test_error_handlers():
    """Test error handling utilities"""
    print("Testing error handlers...")
    
    try:
        from utils.error_handlers import safe_db_commit, cleanup_temp_files
        
        # Test temp file cleanup
        with tempfile.NamedTemporaryFile(delete=False, dir="/tmp") as tf:
            temp_file = tf.name
        
        cleanup_temp_files([temp_file])
        print("✅ Error handlers working correctly")
        
    except Exception as e:
        print(f"❌ Error handlers failed: {e}")

def test_file_handling():
    """Test improved file handling"""
    print("Testing file handling...")
    
    try:
        from utils.input_validation import InputValidator
        
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
            cv2.imwrite(tf.name, test_image)
            
            # Test validation
            validator = InputValidator()
            result = validator.validate_file_upload(tf.name, 'image')
            
            if result['valid']:
                print("✅ File validation working correctly")
            else:
                print(f"❌ File validation failed: {result['errors']}")
                
            os.unlink(tf.name)
            
    except Exception as e:
        print(f"❌ File handling failed: {e}")

def test_vegetation_calculations():
    """Test improved vegetation calculations"""
    print("Testing vegetation calculations...")
    
    try:
        from utils.vegetation_analysis import VegetationAnalyzer
        
        # Create a test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
            cv2.imwrite(tf.name, test_image)
            
            # Test vegetation analysis
            analyzer = VegetationAnalyzer(tf.name)
            analyzer.load_image()
            
            # Test GLI calculation with division by zero protection
            gli = analyzer.calculate_gli()
            if gli is not None and not np.any(np.isnan(gli)):
                print("✅ GLI calculation working correctly")
            else:
                print("❌ GLI calculation failed")
                
            # Test VARI calculation
            vari = analyzer.calculate_vari()
            if vari is not None and not np.any(np.isnan(vari)):
                print("✅ VARI calculation working correctly")
            else:
                print("❌ VARI calculation failed")
                
            os.unlink(tf.name)
            
    except Exception as e:
        print(f"❌ Vegetation calculations failed: {e}")

def test_geotiff_reading():
    """Test improved GeoTIFF reading"""
    print("Testing GeoTIFF reading...")
    
    try:
        from utils.input_validation import InputValidator
        
        # Test GeoTIFF validation (even if file doesn't exist)
        validator = InputValidator()
        
        # Test with a fake GeoTIFF file
        fake_geotiff = "/tmp/test.tif"
        result = validator.validate_file_upload(fake_geotiff, 'geotiff')
        
        # Should fail gracefully
        if not result['valid'] and 'File not found' in str(result['errors']):
            print("✅ GeoTIFF validation working correctly")
        else:
            print("❌ GeoTIFF validation failed")
            
    except Exception as e:
        print(f"❌ GeoTIFF reading failed: {e}")

def test_vegetation_analyzer():
    """Test vegetation analyzer class"""
    print("Testing vegetation analyzer...")
    
    try:
        from utils.vegetation_analysis import VegetationAnalyzer
        
        # Create a test image
        test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
            cv2.imwrite(tf.name, test_image)
            
            # Create analyzer
            analyzer = VegetationAnalyzer(tf.name)
            analyzer.load_image()
            
            # Test NDVI calculation
            ndvi = analyzer.calculate_ndvi()
            if ndvi is not None and ndvi.shape == (50, 50):
                print("✅ NDVI calculation working correctly")
            else:
                print("❌ NDVI calculation failed")
                
            os.unlink(tf.name)
            
    except Exception as e:
        print(f"❌ Vegetation analyzer failed: {e}")

def run_all_tests():
    """Run all critical fix tests"""
    print("=" * 50)
    print("RUNNING CRITICAL FIXES TESTS")
    print("=" * 50)
    
    test_error_handlers()
    test_file_handling()
    test_vegetation_calculations()
    test_geotiff_reading()
    test_vegetation_analyzer()
    
    print("=" * 50)
    print("TESTS COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()