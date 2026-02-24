# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from celery import shared_task
from django.utils import timezone

from detection.models import DetectionResult
from dron_map.models import Projects
from reports.models import GeneratedReport
from reports.generators.pdf_detection import generate_detection_pdf
from reports.generators.pdf_drone import generate_drone_pdf
from reports.generators.excel_report import generate_detection_excel, generate_drone_excel

logger = logging.getLogger(__name__)


@shared_task
def generate_detection_report(detection_result_id: int, formats: list) -> dict:
    """
    Generates reports for a given DetectionResult in specified formats.
    """
    results = {}
    try:
        detection_result = DetectionResult.objects.get(pk=detection_result_id)
    except DetectionResult.DoesNotExist:
        logger.error(f"DetectionResult {detection_result_id} not found.")
        return results

    for fmt in formats:
        # Create a GeneratedReport record with status "processing"
        report_record = GeneratedReport.objects.create(
            report_type="detection",
            format=fmt,
            status="processing",
            detection_result=detection_result,
            # created_by could be passed if needed, currently None
        )
        
        try:
            file_path = None
            if fmt == "pdf":
                file_path = generate_detection_pdf(detection_result)
            elif fmt == "xlsx":
                # generate_detection_excel expects a QuerySet or list
                file_path = generate_detection_excel([detection_result])
            
            if file_path:
                report_record.file_path = file_path
                report_record.status = "ready"
                report_record.completed_at = timezone.now()
                report_record.save()
                results[fmt] = file_path
            else:
                report_record.status = "failed"
                report_record.error_message = "Unsupported format or generation failed."
                report_record.save()
                
        except Exception as e:
            logger.exception(f"Failed to generate {fmt} report for DetectionResult {detection_result_id}")
            report_record.status = "failed"
            report_record.error_message = str(e)
            report_record.save()

    return results


@shared_task
def generate_drone_report(project_id: int, analysis_data: dict, formats: list) -> dict:
    """
    Generates reports for a given Project (Drone Analysis) in specified formats.
    analysis_data is passed directly as it might be computed on the fly or stored elsewhere.
    """
    results = {}
    try:
        project = Projects.objects.get(pk=project_id)
    except Projects.DoesNotExist:
        logger.error(f"Project {project_id} not found.")
        return results

    for fmt in formats:
        # Create a GeneratedReport record with status "processing"
        report_record = GeneratedReport.objects.create(
            report_type="drone",
            format=fmt,
            status="processing",
            project=project,
            # created_by could be passed if needed
        )

        try:
            file_path = None
            if fmt == "pdf":
                file_path = generate_drone_pdf(project, analysis_data)
            elif fmt == "xlsx":
                file_path = generate_drone_excel(project, analysis_data)
            
            if file_path:
                report_record.file_path = file_path
                report_record.status = "ready"
                report_record.completed_at = timezone.now()
                report_record.save()
                results[fmt] = file_path
            else:
                report_record.status = "failed"
                report_record.error_message = "Unsupported format or generation failed."
                report_record.save()
                
        except Exception as e:
            logger.exception(f"Failed to generate {fmt} report for Project {project_id}")
            report_record.status = "failed"
            report_record.error_message = str(e)
            report_record.save()

    return results
