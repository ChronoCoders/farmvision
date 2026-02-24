# -*- coding: utf-8 -*-
import json
import logging
import os
import mimetypes

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from .models import GeneratedReport
from .tasks import generate_detection_report, generate_drone_report
from analysis_logger.service import get_latest_analysis_data

logger = logging.getLogger(__name__)


@login_required
@require_GET
def report_list(request):
    """
    Tüm GeneratedReport kayıtlarını listele.
    """
    reports = GeneratedReport.objects.all().order_by("-created_at")
    return render(request, "reports/report_list.html", {"reports": reports})


@login_required
@require_POST
def request_detection_report(request):
    """
    JSON body: {"detection_result_id": int, "formats": ["pdf", "xlsx"]}
    generate_detection_report.delay(...) çağır, task_id ile 202 döndür.
    """
    try:
        data = json.loads(request.body)
        detection_result_id = data.get("detection_result_id")
        formats = data.get("formats", ["pdf"])

        if not detection_result_id:
            return JsonResponse({"error": "detection_result_id is required"}, status=400)

        task = generate_detection_report.delay(detection_result_id, formats=formats)
        return JsonResponse({"task_id": task.id, "message": "Report generation started"}, status=202)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error requesting detection report: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def request_drone_report(request):
    """
    JSON body: {"project_id": int, "formats": ["pdf", "xlsx"]}
    analysis_logger.service.get_latest_analysis_data(project_id) ile analiz verisini çek,
    generate_drone_report.delay(...) çağır.
    """
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        formats = data.get("formats", ["pdf"])

        if not project_id:
            return JsonResponse({"error": "project_id is required"}, status=400)

        # Analiz verisini çek
        analysis_data = get_latest_analysis_data(project_id)
        if not analysis_data:
             return JsonResponse({"error": "No analysis data found for this project"}, status=404)

        task = generate_drone_report.delay(project_id, analysis_data, formats=formats)
        return JsonResponse({"task_id": task.id, "message": "Drone report generation started"}, status=202)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error requesting drone report: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def download_report(request, report_id):
    """
    GeneratedReport'u bul, status="ready" değilse 404 döndür.
    Path traversal kontrolü yap. FileResponse ile sun.
    """
    report = get_object_or_404(GeneratedReport, pk=report_id)

    if report.status != "ready" or not report.file_path:
        raise Http404("Report is not ready or file is missing.")

    file_path = report.file_path
    
    # Path traversal check
    # Ensure file_path is within MEDIA_ROOT or trusted directory
    # report.file_path is usually relative to MEDIA_ROOT, so we construct full path
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Normalize paths
    full_path = os.path.abspath(full_path)
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    
    if not full_path.startswith(media_root):
        # Security check failed
        logger.warning(f"Path traversal attempt blocked: {full_path}")
        raise Http404("Invalid file path.")

    if not os.path.exists(full_path):
        raise Http404("File does not exist on disk.")

    # Determine content type
    content_type, encoding = mimetypes.guess_type(full_path)
    if report.format == "pdf":
        content_type = "application/pdf"
    elif report.format == "xlsx":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    if not content_type:
        content_type = "application/octet-stream"

    response = FileResponse(open(full_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{os.path.basename(full_path)}"'
    return response


@login_required
@require_POST
def delete_report(request, report_id):
    """
    Deletes a generated report and its file.
    """
    report = get_object_or_404(GeneratedReport, id=report_id)
    
    # Optional: Check if user has permission to delete this report
    
    # Delete file if exists
    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except OSError:
            pass # Log error
            
    report.delete()
    return JsonResponse({"message": "Rapor başarıyla silindi."}, status=200)
