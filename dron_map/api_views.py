# -*- coding: utf-8 -*-
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Projects
from .serializers import ProjectSerializer, ProjectSummarySerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for drone mapping projects

    Provides CRUD operations for farm projects:
    - List all projects (GET /api/projects/)
    - Retrieve single project (GET /api/projects/{id}/)
    - Create new project (POST /api/projects/)
    - Update project (PUT/PATCH /api/projects/{id}/)
    - Delete project (DELETE /api/projects/{id}/)
    - Filter by farm/field/state (GET /api/projects/?Farm=MyFarm)
    - Search by farm/field/title (GET /api/projects/?search=apple)
    - Get project summary (GET /api/projects/{id}/summary/)
    - List by farm (GET /api/projects/by_farm/)

    Note: Authentication required for all endpoints to protect farm data.
    """

    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["Farm", "Field", "State"]
    search_fields = ["Farm", "Field", "Title"]
    ordering_fields = ["Data_time", "Farm", "Field"]
    ordering = ["-Data_time"]

    def get_serializer_class(self):
        """Use summary serializer for list action"""
        if self.action == "list":
            return ProjectSummarySerializer
        return ProjectSerializer

    @action(detail=False, methods=["get"])
    def by_farm(self, request):
        """
        Get projects grouped by farm
        GET /api/projects/by_farm/
        """
        from django.db.models import Count

        farms = Projects.objects.values("Farm").annotate(project_count=Count("id")).order_by("Farm")

        result = []
        for farm_data in farms:
            farm_name = farm_data["Farm"]
            projects = Projects.objects.filter(Farm=farm_name)
            serializer = ProjectSummarySerializer(projects, many=True)
            result.append(
                {
                    "farm": farm_name,
                    "project_count": farm_data["project_count"],
                    "projects": serializer.data,
                }
            )

        return Response(result)

    @action(detail=False, methods=["get"])
    def by_state(self, request):
        """
        Get projects grouped by state
        GET /api/projects/by_state/
        """
        from django.db.models import Count

        states = Projects.objects.values("State").annotate(project_count=Count("id")).order_by("State")

        return Response(states)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """
        Get detailed project summary
        GET /api/projects/{id}/summary/
        """
        project = self.get_object()
        return Response(
            {
                "id": project.id,
                "farm": project.Farm,
                "field": project.Field,
                "title": project.Title,
                "state": project.State,
                "created": project.Data_time,
                "has_picture": bool(project.picture),
                "hashing_path": project.hashing_path,
            }
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get project statistics
        GET /api/projects/statistics/
        """
        from django.db.models import Count

        stats = {
            "total_projects": Projects.objects.count(),
            "total_farms": Projects.objects.values("Farm").distinct().count(),
            "total_fields": Projects.objects.values("Field").distinct().count(),
            "projects_by_state": list(Projects.objects.values("State").annotate(count=Count("id"))),
        }

        return Response(stats)
