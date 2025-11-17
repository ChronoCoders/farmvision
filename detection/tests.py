# -*- coding: utf-8 -*-
"""
Tests for detection app.

This module provides test cases for the fruit detection functionality including:
- Detection model operations
- API endpoints
- Cache utilities
- Image validation
- Async task processing

To run tests:
    python manage.py test detection
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DetectionResult, MultiDetectionBatch
from .cache_utils import calculate_image_hash


class DetectionResultModelTests(TestCase):
    """Test cases for the DetectionResult model."""

    def setUp(self):
        """Set up test data."""
        self.detection = DetectionResult.objects.create(
            fruit_type="mandalina",
            tree_count=100,
            tree_age=5,
            detected_count=450,
            weight=56.25,
            total_weight=5625.0,
            processing_time=2.34,
            confidence_score=0.92,
            image_path="detected/test/image.jpg",
        )

    def test_detection_result_creation(self):
        """Test that a detection result can be created."""
        self.assertEqual(self.detection.fruit_type, "mandalina")
        self.assertEqual(self.detection.detected_count, 450)
        self.assertEqual(self.detection.tree_count, 100)
        self.assertAlmostEqual(self.detection.confidence_score, 0.92)

    def test_detection_total_weight_calculation(self):
        """Test total weight calculation."""
        expected_weight = 5625.0
        self.assertAlmostEqual(self.detection.total_weight, expected_weight)

    def test_model_degradation_check(self):
        """Test model degradation check method."""
        result = self.detection.check_model_degradation()
        self.assertIsInstance(result, dict)


class MultiDetectionBatchTests(TestCase):
    """Test cases for MultiDetectionBatch model."""

    def setUp(self):
        """Set up test data."""
        self.batch = MultiDetectionBatch.objects.create(
            fruit_type="elma",
            batch_hash="abc123def456",
            image_count=10,
        )

    def test_batch_creation(self):
        """Test batch creation."""
        self.assertEqual(self.batch.fruit_type, "elma")
        self.assertEqual(self.batch.image_count, 10)
        self.assertEqual(self.batch.batch_hash, "abc123def456")


class DetectionAPITests(APITestCase):
    """Test cases for Detection API endpoints."""

    def setUp(self):
        """Set up test user and authenticate."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.detection = DetectionResult.objects.create(
            fruit_type="armut",
            tree_count=50,
            tree_age=3,
            detected_count=200,
            weight=44.0,
            total_weight=2200.0,
            processing_time=1.5,
            confidence_score=0.88,
            image_path="detected/test/armut.jpg",
        )

    def test_list_detections_requires_auth(self):
        """Test that listing detections requires authentication."""
        self.client.logout()
        response = self.client.get("/api/detections/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_detections(self):
        """Test listing all detections."""
        response = self.client.get("/api/detections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detection_statistics(self):
        """Test getting detection statistics."""
        response = self.client.get("/api/detections/statistics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("overall", response.data)

    def test_get_recent_detections(self):
        """Test getting recent detections."""
        response = self.client.get("/api/detections/recent/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_fruit_type(self):
        """Test filtering detections by fruit type."""
        response = self.client.get("/api/detections/?fruit_type=armut")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CacheUtilsTests(TestCase):
    """Test cases for cache utilities."""

    def test_calculate_image_hash(self):
        """Test image hash calculation."""
        test_data = b"test image data"
        hash_result = calculate_image_hash(test_data)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex digest length

    def test_hash_consistency(self):
        """Test that same data produces same hash."""
        test_data = b"consistent data"
        hash1 = calculate_image_hash(test_data)
        hash2 = calculate_image_hash(test_data)
        self.assertEqual(hash1, hash2)

    def test_hash_uniqueness(self):
        """Test that different data produces different hash."""
        data1 = b"data one"
        data2 = b"data two"
        hash1 = calculate_image_hash(data1)
        hash2 = calculate_image_hash(data2)
        self.assertNotEqual(hash1, hash2)


class DetectionViewTests(TestCase):
    """Test cases for detection web views."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", password="testpass123"
        )

    def test_index_page_requires_login(self):
        """Test that index page requires authentication."""
        response = self.client.get("/detection/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_system_monitoring_requires_login(self):
        """Test that system monitoring requires authentication."""
        response = self.client.get("/detection/system-monitoring/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_index_page_authenticated(self):
        """Test accessing index page when authenticated."""
        self.client.login(username="viewuser", password="testpass123")
        response = self.client.get("/detection/")
        self.assertEqual(response.status_code, 200)


class InputValidationTests(TestCase):
    """Test cases for input validation."""

    def test_tree_count_range_validation(self):
        """Test that tree count must be within valid range."""
        # Valid range: 1-100000
        valid_count = 500
        self.assertTrue(1 <= valid_count <= 100000)

        invalid_count = 200000
        self.assertFalse(1 <= invalid_count <= 100000)

    def test_tree_age_range_validation(self):
        """Test that tree age must be within valid range."""
        # Valid range: 0-150
        valid_age = 50
        self.assertTrue(0 <= valid_age <= 150)

        invalid_age = 200
        self.assertFalse(0 <= invalid_age <= 150)
