#!/usr/bin/env python3
"""
Test script for the critical debugging fixes
"""

import sys
import os
sys.path.append('.')

from utils.error_handlers import safe_db_commit, validate_form_inputs, cleanup_temp_files
from utils.helpers import save_uploaded_file, allowed_file
from utils.advanced_vegetation import apply_colormap, calculate_ndvi_advanced
from utils.histogram_geotiff import read_geotiff
from utils.vegetation_analysis import VegetationAnalyzer
import numpy as np
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_error_handlers():
    """Test error handling utilities"""
    logger.info("Testing error handlers...")
    
    # Test form validation
    missing = validate_form_inputs(['name', 'email'], {'name': 'test'})
    assert 'email' in missing, "Form validation failed"
    
    # Test file cleanup
    temp_files = []
    cleanup_temp_files(temp_files)  # Should not fail
    
    logger.info("✅ Error handlers working")

def test_file_handling():
    """Test improved file handling"""
    logger.info("Testing file handling...")
    
    # Test file extension validation
    assert allowed_file('test.jpg') == True, "JPG files should be allowed"
    assert allowed_file('test.exe') == False, "EXE files should not be allowed"
    
    logger.info("✅ File handling working")

def test_vegetation_calculations():
    """Test improved vegetation calculations"""
    logger.info("Testing vegetation calculations...")
    
    # Test NDVI calculation with proper error handling
    red_band = np.random.rand(100, 100) * 255
    nir_band = np.random.rand(100, 100) * 255
    
    ndvi = calculate_ndvi_advanced(red_band, nir_band)
    assert ndvi is not None, "NDVI calculation failed"
    assert ndvi.shape == (100, 100), "NDVI shape incorrect"
    
    # Test colormap application
    test_data = np.random.rand(50, 50)
    colored = apply_colormap(test_data, 'rdylgn')
    assert colored is not None, "Colormap application failed"
    
    logger.info("✅ Vegetation calculations working")

def test_geotiff_reading():
    """Test improved GeoTIFF reading"""
    logger.info("Testing GeoTIFF reading...")
    
    # Test with non-existent file
    data, metadata = read_geotiff('nonexistent.tif')
    assert data is None, "Should return None for non-existent files"
    
    logger.info("✅ GeoTIFF reading working")

def test_vegetation_analyzer():
    """Test vegetation analyzer class"""
    logger.info("Testing vegetation analyzer...")
    
    # Create a test image
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        import cv2
        cv2.imwrite(tmp_file.name, test_image)
        
        try:
            analyzer = VegetationAnalyzer(tmp_file.name)
            ndvi = analyzer.calculate_ndvi()
            assert ndvi is not None, "NDVI calculation should not fail"
            assert ndvi.shape == (100, 100), "NDVI shape should match image"
            logger.info("✅ Vegetation analyzer working")
        finally:
            os.unlink(tmp_file.name)

def run_all_tests():
    """Run all critical fix tests"""
    logger.info("=== Testing Critical Debugging Fixes ===")
    
    tests = [
        test_error_handlers,
        test_file_handling,
        test_vegetation_calculations,
        test_geotiff_reading,
        test_vegetation_analyzer
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            logger.error(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    logger.info(f"\n=== Results ===")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    if failed == 0:
        logger.info("🎉 All critical fixes working!")
    else:
        logger.warning(f"⚠️  {failed} tests failed")

if __name__ == "__main__":
    run_all_tests()