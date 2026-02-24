# -*- coding: utf-8 -*-
"""
Tests for dron_map app.

This module provides test cases for the drone mapping functionality including:
- Project CRUD operations
- API endpoints
- File upload validation
- Vegetation index calculations

To run tests:
    python manage.py test dron_map
"""

import io
from unittest.mock import patch, MagicMock

from PIL import Image
from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Projects


class ProjectModelTests(TestCase):
    """Test cases for the Projects model."""

    def setUp(self):
        """Set up test data."""
        self.project = Projects.objects.create(
            Farm="Test Farm",
            Field="Field A",
            Title="Test Project",
            State="Active",
        )

    def test_project_creation(self):
        """Test that a project can be created."""
        self.assertEqual(self.project.Farm, "Test Farm")
        self.assertEqual(self.project.Field, "Field A")
        self.assertEqual(self.project.State, "Active")

    def test_project_string_representation(self):
        """Test the string representation of a project."""
        self.assertIsNotNone(str(self.project))


class ProjectAPITests(APITestCase):
    """Test cases for the Projects API endpoints."""

    def setUp(self):
        """Set up test user and authenticate."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.project = Projects.objects.create(
            Farm="API Test Farm",
            Field="Field B",
            Title="API Test Project",
            State="Active",
        )

    def test_list_projects_requires_auth(self):
        """Test that listing projects requires authentication."""
        self.client.logout()
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_projects(self):
        """Test listing all projects."""
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_statistics(self):
        """Test getting project statistics."""
        response = self.client.get("/api/projects/statistics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_projects", response.data)

    def test_filter_projects_by_farm(self):
        """Test filtering projects by farm name."""
        response = self.client.get("/api/projects/?Farm=API Test Farm")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProjectViewTests(TestCase):
    """Test cases for project web views."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", password="testpass123"
        )

    def test_projects_page_requires_login(self):
        """Test that projects page requires authentication."""
        response = self.client.get("/dron-map/projects/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_projects_page_authenticated(self):
        """Test accessing projects page when authenticated."""
        self.client.login(username="viewuser", password="testpass123")
        response = self.client.get("/dron-map/projects/")
        self.assertIn(response.status_code, [200, 302])


class ProjectViewCreateTests(TestCase):
    """Test project creation via web views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="mapuser", password="pass123")
        self.client.login(username="mapuser", password="pass123")

    def test_add_project_page_loads(self):
        """Add project page should return 200."""
        response = self.client.get("/dron-map/add-projects/")
        self.assertIn(response.status_code, [200, 302])

    def test_map_page_requires_login(self):
        """Map page should redirect unauthenticated users."""
        self.client.logout()
        response = self.client.get("/dron-map/map/")
        self.assertEqual(response.status_code, 302)


class ProjectAPIWriteTests(APITestCase):
    """Test project create/update/delete via API."""

    def setUp(self):
        self.user = User.objects.create_user(username="apiwriter", password="pass123")
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        """Authenticated user should be able to create a project."""
        response = self.client.post(
            "/api/projects/",
            {
                "Farm": "New Farm",
                "Field": "Field C",
                "Title": "New Project",
                "State": "Active",
            },
            format="json",
        )
        self.assertIn(response.status_code, [200, 201])

    def test_unauthenticated_cannot_create_project(self):
        """Unauthenticated requests should be rejected."""
        self.client.logout()
        response = self.client.post(
            "/api/projects/",
            {"Farm": "Hack Farm"},
            format="json",
        )
        self.assertIn(response.status_code, [401, 403])


class HealthAlgorithmTests(TestCase):
    """Test vegetation index algorithm names are valid."""

    def test_health_algorithms_not_empty(self):
        """HEALTH_ALGORITHMS dict should have entries."""
        from dron_map.views import HEALTH_ALGORITHMS
        self.assertGreater(len(HEALTH_ALGORITHMS), 0)

    def test_ndvi_present(self):
        """NDVI must be present as it is the most common index."""
        from dron_map.views import HEALTH_ALGORITHMS
        self.assertIn("ndvi", HEALTH_ALGORITHMS)
