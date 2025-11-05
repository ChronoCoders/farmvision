# -*- coding: utf-8 -*-
"""
Celery tasks for asynchronous image detection processing.

This module contains background tasks for:
- Async image detection
- Model health monitoring
- Batch processing
"""
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from celery import shared_task

from yolowebapp2 import predict_tree
from detection.models import DetectionResult

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

FRUIT_WEIGHTS = {
    "mandalina": 0.125,
    "elma": 0.105,
    "armut": 0.220,
    "seftale": 0.185,
    "nar": 0.300,
}

FRUIT_MODELS = {
    "mandalina": "mandalina.pt",
    "elma": "elma.pt",
    "armut": "armut.pt",
    "seftale": "seftale.pt",
    "nar": "nar.pt",
}


@shared_task(bind=True, name="detection.tasks.process_image_detection")
def process_image_detection(
    self,
    image_path: str,
    fruit_type: str,
    tree_count: int,
    tree_age: int,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Asynchronous image detection task.

    Args:
        self: Celery task instance (for updating state)
        image_path: Path to the uploaded image file
        fruit_type: Type of fruit to detect
        tree_count: Number of trees
        tree_age: Age of trees
        user_id: Optional user ID who initiated the task

    Returns:
        dict: Detection results including count, weight, confidence, etc.

    Raises:
        Exception: If detection fails
    """
    try:
        # Update task state to PROCESSING
        self.update_state(
            state="PROCESSING", meta={"status": "Görüntü işleniyor...", "progress": 10}
        )

        # Validate fruit type
        if fruit_type not in FRUIT_MODELS:
            raise ValueError(f"Geçersiz meyve grubu: {fruit_type}")

        # Get model path
        model_path = FRUIT_MODELS[fruit_type]

        logger.info(
            f"Task {self.request.id}: Starting detection for {fruit_type} "
            f"on image {image_path}"
        )

        # Update state
        self.update_state(
            state="PROCESSING", meta={"status": "Model yükleniyor...", "progress": 30}
        )

        start_time = time.time()

        # Run detection
        try:
            detec, unique_id, confidence_score = predict_tree.preddict(
                path_to_weights=model_path, path_to_source=image_path
            )

            # Extract detection count
            count_str = detec.decode("utf-8")
            detected_count = int(count_str)

        except Exception as e:
            logger.error(f"Task {self.request.id}: Detection failed: {e}")
            raise

        # Update state
        self.update_state(
            state="PROCESSING",
            meta={"status": "Sonuçlar hesaplanıyor...", "progress": 70},
        )

        # Calculate weights
        weight_per_fruit = FRUIT_WEIGHTS[fruit_type]
        weight = detected_count * weight_per_fruit
        total_weight = tree_count * weight
        processing_time = time.time() - start_time

        # Update state
        self.update_state(
            state="PROCESSING",
            meta={"status": "Veritabanına kaydediliyor...", "progress": 90},
        )

        # Save to database
        try:
            detection_result = DetectionResult.objects.create(
                fruit_type=fruit_type,
                tree_count=tree_count,
                tree_age=tree_age,
                detected_count=detected_count,
                weight=weight,
                total_weight=total_weight,
                processing_time=processing_time,
                confidence_score=confidence_score,
                image_path=f"detected/{unique_id}/{Path(image_path).name}",
                task_id=self.request.id,
            )

            logger.info(
                f"Task {self.request.id}: Detection completed. "
                f"Count={detected_count}, Confidence={confidence_score:.3f}"
            )

        except Exception as db_error:
            logger.error(f"Task {self.request.id}: DB save failed: {db_error}")
            # Continue even if DB save fails

        # Clean up temp file
        try:
            if os.path.exists(image_path):
                os.unlink(image_path)
                logger.debug(
                    f"Task {self.request.id}: Cleaned up temp file {image_path}"
                )
        except Exception as cleanup_error:
            logger.warning(f"Task {self.request.id}: Cleanup failed: {cleanup_error}")

        # Return results
        result = {
            "task_id": str(self.request.id),
            "status": "SUCCESS",
            "fruit_type": str(fruit_type),
            "detected_count": int(detected_count),
            "weight": float(weight),
            "total_weight": float(total_weight),
            "confidence_score": float(confidence_score),
            "processing_time": float(processing_time),
            "image_path": f"detected/{unique_id}/{Path(image_path).name}",
            "unique_id": str(unique_id),
            "detection_result_id": (
                int(detection_result.pk) if "detection_result" in locals() else None
            ),
        }

        return result

    except Exception as e:
        logger.error(f"Task {self.request.id}: Fatal error: {e}", exc_info=True)

        # Clean up on failure
        try:
            if os.path.exists(image_path):
                os.unlink(image_path)
        except BaseException:
            pass

        # Update task state to FAILURE with error info
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Hata oluştu",
                "error": str(e),
                "exc_type": type(e).__name__,
            },
        )

        # Re-raise so Celery marks task as failed
        raise


@shared_task(name="detection.tasks.check_model_health")
def check_model_health() -> Dict[str, Any]:
    """
    Periodic task to check model health and degradation.

    This task runs daily via Celery Beat and checks if any
    models are showing signs of degradation.

    Returns:
        dict: Health check results for all models
    """
    logger.info("Starting model health check...")

    fruits = ["mandalina", "elma", "armut", "seftale", "nar"]
    results = {}
    alerts = []

    for fruit in fruits:
        try:
            status = DetectionResult.check_model_degradation(
                fruit_type=fruit, days=7, threshold=0.7
            )

            results[fruit] = status

            if status["is_degraded"]:
                alert_msg = (
                    f"⚠️ Model Degradation Alert: {fruit} "
                    f"confidence={status['avg_confidence']:.3f} "
                    f"(threshold=0.7, samples={status['sample_count']})"
                )
                logger.warning(alert_msg)
                alerts.append(alert_msg)
            else:
                logger.info(
                    f"✅ {fruit}: OK "
                    f"(confidence={status['avg_confidence']:.3f}, "
                    f"samples={status['sample_count']})"
                )

        except Exception as e:
            logger.error(f"Health check failed for {fruit}: {e}")
            results[fruit] = {"error": str(e)}

    return {
        "timestamp": time.time(),
        "results": results,
        "alerts": alerts,
        "overall_healthy": len(alerts) == 0,
    }


@shared_task(bind=True, name="detection.tasks.cleanup_old_results")
def cleanup_old_results(self, days_old: int = 30) -> Dict[str, Any]:
    """
    Cleanup old detection results and associated files.

    Args:
        self: Celery task instance
        days_old: Remove results older than this many days

    Returns:
        dict: Cleanup statistics
    """
    from datetime import timedelta
    from django.utils import timezone

    logger.info(f"Starting cleanup of results older than {days_old} days...")

    cutoff_date = timezone.now() - timedelta(days=days_old)

    try:
        # Get old results
        old_results = DetectionResult.objects.filter(created_at__lt=cutoff_date)
        count = old_results.count()

        # Delete from database
        deleted_count, _ = old_results.delete()

        logger.info(f"Cleanup completed: {deleted_count} records removed")

        return {
            "status": "SUCCESS",
            "deleted_count": int(deleted_count),
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        return {"status": "FAILURE", "error": str(e)}
