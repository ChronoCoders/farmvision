# -*- coding: utf-8 -*-
from django.shortcuts import render
from pathlib import Path
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpResponse, HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.http import require_http_methods
from typing import Dict, Any
import time
import logging
import tempfile
import os
import uuid
import shutil
import magic
from yolowebapp2 import predict_tree, hashing
from detection.cache_utils import (
    calculate_image_hash,
    get_cached_prediction,
    set_cached_prediction,
)
from detection.config import (
    FRUIT_WEIGHTS,
    FRUIT_MODELS,
    validate_tree_count,
    validate_tree_age,
)

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/x-ms-bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def _get_chart_data() -> str:
    """
    Get chart data from recent detection results for dashboard display.

    Returns:
        JSON string containing chart labels and values for monthly averages.
    """
    import json
    from detection.models import DetectionResult
    from django.db.models import Avg
    from django.db.models.functions import TruncMonth
    from datetime import timedelta
    from django.utils import timezone

    # Get last 6 months of data
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_stats = (
        DetectionResult.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(avg_count=Avg("detected_count"))
        .order_by("month")
    )

    chart_labels = []
    chart_values = []
    for stat in monthly_stats:
        chart_labels.append(stat["month"].strftime("%Y-%m"))
        chart_values.append(float(stat["avg_count"]) if stat["avg_count"] else 0)

    return json.dumps(
        {
            "labels": chart_labels if chart_labels else None,
            "values": chart_values if chart_values else None,
            "label": "Aylık Ortalama Tespit Sayısı",
        }
    )


def _validate_detection_form(request: HttpRequest) -> Dict[str, Any]:
    """
    Validate and parse detection form inputs.

    Args:
        request: HTTP request with POST data

    Returns:
        Dictionary with validated form data including:
        - meyve_grubu: str
        - agac_sayisi: int
        - agac_yasi: int
        - ekim_sirasi: str
        - file: UploadedFile

    Raises:
        ValidationError: If any validation fails
    """
    meyve_grubu = request.POST.get("meyve_grubu")
    agac_sayisi = request.POST.get("agac_sayisi")
    agac_yasi = request.POST.get("agac_yasi")
    ekim_sirasi = request.POST.get("ekim_sirasi")
    filename = request.FILES.get("file")

    if not all([meyve_grubu, agac_sayisi, agac_yasi, ekim_sirasi, filename]):
        raise ValidationError("Tüm alanları doldurun")

    if filename is None:
        raise ValidationError("Dosya bulunamadı")

    validate_image_file(filename)

    # Validate tree count
    try:
        if agac_sayisi is None:
            raise ValidationError("Ağaç sayısı gerekli")
        agac_sayisi_int = int(agac_sayisi)
        if not validate_tree_count(agac_sayisi_int):
            raise ValidationError("Ağaç sayısı 1-100000 arasında olmalı")
    except ValueError:
        raise ValidationError("Geçersiz sayı formatı")

    # Validate tree age
    try:
        if agac_yasi is None:
            raise ValidationError("Ağaç yaşı gerekli")
        agac_yasi_int = int(agac_yasi)
        if not validate_tree_age(agac_yasi_int):
            raise ValidationError("Ağaç yaşı 0-150 arasında olmalı")
    except ValueError:
        raise ValidationError("Geçersiz yaş formatı")

    if meyve_grubu not in FRUIT_MODELS:
        raise ValidationError("Geçersiz meyve grubu")

    return {
        "meyve_grubu": meyve_grubu,
        "agac_sayisi": agac_sayisi_int,
        "agac_yasi": agac_yasi_int,
        "ekim_sirasi": ekim_sirasi,
        "file": filename,
    }


def _handle_cached_detection(
    cached_result: Dict[str, Any], agac_sayisi: int
) -> Dict[str, Any]:
    """
    Build response from cached detection result.

    Args:
        cached_result: Cached prediction data
        agac_sayisi: Tree count for total weight calculation

    Returns:
        Response dictionary with detection results
    """
    cached_weight = cached_result["weight_per_fruit"] * cached_result["detected_count"]

    return {
        "count": cached_result["detected_count"],
        "kilo": cached_weight,
        "toplam_agirlik": agac_sayisi * cached_weight,
        "time": "0.00",
        "image": cached_result["image_path"],
        "image_detection": cached_result["image_path"],
        "confidence": f"{cached_result['confidence_score']:.2%}",
        "from_cache": True,
    }


def _save_detection_to_db(
    meyve_grubu: str,
    agac_sayisi: int,
    agac_yasi: int,
    count: int,
    weight: float,
    total_weight: float,
    processing_time: float,
    confidence_score: float,
    image_path: str,
) -> None:
    """
    Save detection result to database.

    Args:
        meyve_grubu: Fruit type
        agac_sayisi: Tree count
        agac_yasi: Tree age
        count: Detected fruit count
        weight: Weight per tree
        total_weight: Total weight for all trees
        processing_time: Time taken for detection
        confidence_score: Model confidence
        image_path: Path to detected image
    """
    from detection.models import DetectionResult

    try:
        DetectionResult.objects.create(
            fruit_type=meyve_grubu,
            tree_count=agac_sayisi,
            tree_age=agac_yasi,
            detected_count=count,
            weight=weight,
            total_weight=total_weight,
            processing_time=processing_time,
            confidence_score=confidence_score,
            image_path=image_path,
        )
        logger.info(
            f"Detection result saved: {meyve_grubu}, count={count}, confidence={confidence_score:.3f}"
        )
    except Exception as db_error:
        logger.error(f"Veritabanı kaydetme hatası: {db_error}")
        # Don't fail the request if DB save fails, just log it


def _process_new_detection(
    form_data: Dict[str, Any], image_data: bytes, image_hash: str, safe_filename: str
) -> Dict[str, Any]:
    """
    Process a new detection (cache miss).

    Args:
        form_data: Validated form data
        image_data: Raw image bytes
        image_hash: SHA256 hash of image
        safe_filename: Sanitized filename

    Returns:
        Response dictionary with detection results

    Raises:
        ValidationError: If detection fails
    """
    temp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(temp_dir, safe_filename)

    # Write uploaded file to temp directory
    try:
        with open(tmp_path, "wb") as tmp:
            tmp.write(image_data)
    except Exception as e:
        logger.error(f"Geçici dosya yazma hatası: {tmp_path}: {e}")
        raise ValidationError("Dosya yüklenirken hata oluştu")

    start_time = time.time()

    try:
        model_path = FRUIT_MODELS[form_data["meyve_grubu"]]
        detec, unique_id, confidence_score = predict_tree.predict(
            path_to_weights=model_path, path_to_source=tmp_path
        )

        count = extract_detection_count(detec)
        weight_per_fruit = FRUIT_WEIGHTS[form_data["meyve_grubu"]]
        processing_time = time.time() - start_time

        weight = count * weight_per_fruit
        total_weight = form_data["agac_sayisi"] * weight
        image_path = f"detected/{unique_id}/{safe_filename}"

        response = {
            "count": count,
            "kilo": weight,
            "toplam_agirlik": total_weight,
            "time": f"{processing_time:.2f}",
            "image": image_path,
            "image_detection": image_path,
            "confidence": f"{confidence_score:.2%}",
            "from_cache": False,
        }

        # Cache the prediction result
        cache_data = {
            "detected_count": count,
            "weight_per_fruit": weight_per_fruit,
            "confidence_score": confidence_score,
            "image_path": image_path,
            "fruit_type": form_data["meyve_grubu"],
            "image_hash": image_hash,
        }
        set_cached_prediction(image_hash, form_data["meyve_grubu"], cache_data)

        # Save detection result to database
        _save_detection_to_db(
            meyve_grubu=form_data["meyve_grubu"],
            agac_sayisi=form_data["agac_sayisi"],
            agac_yasi=form_data["agac_yasi"],
            count=count,
            weight=weight,
            total_weight=total_weight,
            processing_time=processing_time,
            confidence_score=confidence_score,
            image_path=image_path,
        )

        return response

    except (FileNotFoundError, RuntimeError, ValueError, IOError) as e:
        logger.error(f"Model algılama hatası: {e}")
        raise ValidationError("Algılama işlemi başarısız oldu. Lütfen tekrar deneyin.")
    finally:
        # Clean up temp file
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Geçici dosya silme hatası: {tmp_path}: {e}")


def validate_image_file(file: UploadedFile) -> bool:
    if not file:
        raise ValidationError("Dosya bulunamadı")

    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise ValidationError("Dosya boyutu çok büyük (maksimum 10MB)")

    # Extract basename to prevent path traversal
    if file.name is None:
        raise ValidationError("Dosya adı bulunamadı")

    filename = os.path.basename(file.name)

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"Path traversal attempt detected: {file.name}")
        raise ValidationError("Geçersiz dosya adı")

    # Check file extension
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Geçersiz dosya formatı")

    # Check actual file MIME type using magic bytes
    try:
        # Read first chunk of file to check MIME type
        file.seek(0)
        file_header = file.read(2048)
        file.seek(0)  # Reset file pointer

        mime = magic.from_buffer(file_header, mime=True)

        if mime not in ALLOWED_MIME_TYPES:
            logger.warning(
                f"MIME type mismatch: expected image, got {mime} for file {file.name}"
            )
            raise ValidationError(f"Geçersiz dosya tipi: {mime}")

    except Exception as e:
        logger.error(f"Magic bytes check failed for {file.name}: {e}")
        raise ValidationError("Dosya doğrulama hatası")

    return True


def extract_detection_count(detec_result: bytes) -> int:
    try:
        count_str = detec_result.decode("utf-8")
        return int(count_str)
    except (ValueError, UnicodeDecodeError, AttributeError) as e:
        logger.error(f"Algılama sonucu parse hatası: {e}")
        raise ValidationError("Algılama sonucu işlenemedi")


def sanitize_filename(filename: str) -> str:
    # Extract basename to prevent path traversal
    filename = os.path.basename(filename)

    # Additional check for path traversal - reject if malicious path detected
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(
            f"Path traversal attempt detected in sanitize_filename: {filename}"
        )
        raise ValidationError("Geçersiz dosya adı - güvenlik ihlali tespit edildi")

    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))

    # Ensure extension is safe
    if not ext or len(ext) > 10:
        ext = ".jpg"

    return f"{uuid.uuid4().hex}_{safe_name[:50]}{ext.lower()}"


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """
    Main detection view for single image fruit detection.

    Handles both GET (display form) and POST (process detection) requests.
    Uses caching for improved performance on repeated images.
    """
    response: Dict[str, Any] = {}
    chart_data = _get_chart_data()

    if request.method == "POST":
        try:
            # Validate form inputs
            form_data = _validate_detection_form(request)
            filename = form_data["file"]

            # Prepare image data for caching
            safe_filename = sanitize_filename(filename.name or "")
            filename.seek(0)
            image_data = filename.read()
            filename.seek(0)

            # Calculate image hash for cache lookup
            image_hash = calculate_image_hash(image_data)

            # Check cache first
            cached_result = get_cached_prediction(image_hash, form_data["meyve_grubu"])

            if cached_result:
                # Cache HIT
                logger.info(
                    f"Using cached result for {form_data['meyve_grubu']}, hash={image_hash[:16]}..."
                )
                response = _handle_cached_detection(
                    cached_result, form_data["agac_sayisi"]
                )
            else:
                # Cache MISS - run prediction
                response = _process_new_detection(
                    form_data, image_data, image_hash, safe_filename
                )

        except ValidationError as e:
            return render(request, "main.html", {"error": str(e), "chart_data": chart_data})
        except Exception as e:
            logger.error(f"İşlem hatası: {e}")
            return render(
                request,
                "main.html",
                {"error": "Bir hata oluştu", "chart_data": chart_data},
            )

    context: Dict[str, Any] = {"chart_data": chart_data}
    if response:
        context["response"] = response
    return render(request, "main.html", context)


def _validate_multi_detection_form(request: HttpRequest) -> Dict[str, Any]:
    """
    Validate and parse multi-detection form inputs.

    Args:
        request: HTTP request with POST data

    Returns:
        Dictionary with validated form data

    Raises:
        ValidationError: If validation fails
    """
    meyve_grubu = request.POST.get("meyve_grubu")
    ekim_sirasi = request.POST.get("ekim_sirasi")
    filelist = request.FILES.getlist("file")

    if not meyve_grubu or not ekim_sirasi or not filelist:
        raise ValidationError("Tüm alanları doldurun")

    for file in filelist:
        validate_image_file(file)

    if meyve_grubu not in FRUIT_MODELS:
        raise ValidationError("Geçersiz meyve grubu")

    return {
        "meyve_grubu": meyve_grubu,
        "ekim_sirasi": ekim_sirasi,
        "filelist": filelist,
    }


def _save_uploaded_files(filelist: list, upload_dir: Path) -> None:
    """
    Save uploaded files to directory with path traversal protection.

    Args:
        filelist: List of uploaded files
        upload_dir: Directory to save files to

    Raises:
        ValidationError: If file saving fails
    """
    for image in filelist:
        if not image.name:
            raise ValidationError("Dosya adı bulunamadı")

        safe_image_name = os.path.basename(image.name)
        if ".." in safe_image_name or "/" in safe_image_name or "\\" in safe_image_name:
            logger.warning(f"Path traversal attempt in filename: {image.name}")
            raise ValidationError(f"Geçersiz dosya adı: {image.name}")

        img_path = upload_dir / safe_image_name
        with open(img_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)


def _cleanup_directory(directory: Path) -> None:
    """
    Clean up a directory and its contents.

    Args:
        directory: Path to directory to remove
    """
    if directory and directory.exists():
        try:
            shutil.rmtree(str(directory))
            logger.info(f"Dosyalar temizlendi: {directory}")
        except Exception as cleanup_error:
            logger.error(f"Dosya temizleme hatası: {cleanup_error}")


@login_required
def multi_detection_image(request: HttpRequest) -> HttpResponse:
    """
    Multi-image detection view for batch fruit detection.

    Processes multiple images at once and generates a combined result.
    """
    if request.method != "POST":
        return render(request, "multi_detection_fruit.html")

    try:
        # Validate form inputs
        form_data = _validate_multi_detection_form(request)

        # Create hash and output directory
        try:
            hass = hashing.add_prefix2(filename=f"{time.time()}")
        except Exception as e:
            logger.error(f"Hash oluşturma hatası: {e}")
            raise ValidationError("Dizin oluşturulamadı")

        upload_dir = Path(hass[0])
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Çıktı dizini oluşturma hatası: {hass[0]}: {e}")
            raise ValidationError("Çıktı dizini oluşturulamadı")

        # Save uploaded files
        try:
            _save_uploaded_files(form_data["filelist"], upload_dir)
        except Exception as e:
            logger.error(f"Dosya kaydetme hatası: {e}")
            _cleanup_directory(upload_dir)
            raise ValidationError("Dosyalar kaydedilemedi")

        # Run multi prediction
        try:
            weight_file = FRUIT_MODELS[form_data["meyve_grubu"]]
            predict_tree.multi_predictor(
                path_to_weights=weight_file,
                path_to_source=hass[0],
                ekim_sirasi=form_data["ekim_sirasi"],
                hashing=hass[1],
            )
            return render(request, "multi_detection_fruit.html", {"response": hass[1]})

        except (FileNotFoundError, RuntimeError, ValueError, IOError) as e:
            logger.error(f"Çoklu algılama işlemi hatası: {e}")
            _cleanup_directory(upload_dir)
            raise ValidationError("Algılama başarısız oldu. Lütfen tekrar deneyin.")

    except ValidationError as e:
        return render(request, "multi_detection_fruit.html", {"error": str(e)})
    except Exception as e:
        logger.error(f"Çoklu algılama hatası: {e}")
        return render(request, "multi_detection_fruit.html", {"error": "Bir hata oluştu"})


@login_required
def download_image(request: HttpRequest, slug: str) -> FileResponse | HttpResponse:
    try:
        safe_slug = "".join(c for c in slug if c.isalnum() or c in ("-", "_"))
        if safe_slug != slug:
            return HttpResponse("Geçersiz dosya adı", status=400)

        file_path = (BASE_DIR / "media" / f"{safe_slug}_result.zip").resolve()
        media_dir = (BASE_DIR / "media").resolve()

        if not str(file_path).startswith(str(media_dir)):
            return HttpResponse("Geçersiz dosya yolu", status=400)

        if not file_path.exists():
            return HttpResponse("Dosya bulunamadı", status=404)

        # Open file and let FileResponse handle closure properly
        file_handle = open(file_path, "rb")
        response = FileResponse(
            file_handle,
            as_attachment=True,
            filename=f"{safe_slug}_result.zip",
        )
        # FileResponse will automatically close the file when done
        return response
    except Exception as e:
        logger.error(f"Dosya indirme hatası: {e}")
        return HttpResponse("Dosya indirilemedi", status=500)


@login_required
def system_monitoring(request: HttpRequest) -> HttpResponse:
    """System monitoring dashboard with Turkish localization"""
    import psutil
    import platform
    from datetime import datetime

    try:
        # CPU Usage - CPU Kullanımı
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Memory Usage - Bellek Kullanımı
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024**3)
        memory_used_gb = memory.used / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        memory_percent = memory.percent

        # Disk Usage - Disk Kullanımı
        disk = psutil.disk_usage("/")
        disk_total_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)
        disk_free_gb = disk.free / (1024**3)
        disk_percent = disk.percent

        # System Info - Sistem Bilgisi
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        # Boot time - Başlangıç Zamanı
        from django.utils import timezone

        boot_time = timezone.make_aware(datetime.fromtimestamp(psutil.boot_time()))
        uptime = timezone.now() - boot_time
        uptime_str = f"{uptime.days} gün, {uptime.seconds // 3600} saat, {(uptime.seconds % 3600) // 60} dakika"

        # Calculate uptime percentage (based on 30-day milestone, capped at 100%)
        uptime_days = uptime.days + (uptime.seconds / 86400)
        uptime_percent = min(100, (uptime_days / 30) * 100)

        # Model Status - Model Durumu
        from detection.model_registry import get_loaded_models_info

        loaded_models = get_loaded_models_info()

        context = {
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "cpu_freq": cpu_freq.current if cpu_freq else 0,
            "memory_total_gb": f"{memory_total_gb:.2f}",
            "memory_used_gb": f"{memory_used_gb:.2f}",
            "memory_available_gb": f"{memory_available_gb:.2f}",
            "memory_percent": memory_percent,
            "disk_total_gb": f"{disk_total_gb:.2f}",
            "disk_used_gb": f"{disk_used_gb:.2f}",
            "disk_free_gb": f"{disk_free_gb:.2f}",
            "disk_percent": disk_percent,
            "system_info": system_info,
            "boot_time": boot_time,
            "uptime_str": uptime_str,
            "uptime_days": uptime_days,
            "uptime_percent": uptime_percent,
            "loaded_models": loaded_models,
        }

        return render(request, "system_monitoring.html", context)

    except Exception as e:
        logger.error(f"Sistem izleme hatası: {e}")
        return render(
            request,
            "system_monitoring.html",
            {"error": f"Sistem bilgileri alınamadı: {str(e)}"},
        )


def _validate_async_detection_form(request: HttpRequest) -> Dict[str, Any]:
    """
    Validate async detection form inputs.

    Args:
        request: HTTP request with POST data

    Returns:
        Dictionary with validated form data

    Raises:
        ValidationError: If validation fails
    """
    meyve_grubu = request.POST.get("meyve_grubu")
    agac_sayisi = request.POST.get("agac_sayisi")
    agac_yasi = request.POST.get("agac_yasi")
    filename = request.FILES.get("file")

    if not all([meyve_grubu, agac_sayisi, agac_yasi, filename]):
        raise ValidationError("Tüm alanları doldurun")

    if filename is None:
        raise ValidationError("Dosya bulunamadı")

    validate_image_file(filename)

    try:
        if agac_sayisi is None or agac_yasi is None:
            raise ValidationError("Ağaç sayısı ve yaşı gerekli")
        agac_sayisi_int = int(agac_sayisi)
        agac_yasi_int = int(agac_yasi)
    except ValueError:
        raise ValidationError("Geçersiz sayı formatı")

    if meyve_grubu not in FRUIT_MODELS:
        raise ValidationError("Geçersiz meyve grubu")

    return {
        "meyve_grubu": meyve_grubu,
        "agac_sayisi": agac_sayisi_int,
        "agac_yasi": agac_yasi_int,
        "file": filename,
    }


def _build_cached_async_response(
    cached_result: Dict[str, Any], agac_sayisi: int
) -> JsonResponse:
    """
    Build JSON response for cached async detection result.

    Args:
        cached_result: Cached prediction data
        agac_sayisi: Tree count for total weight calculation

    Returns:
        JsonResponse with cached detection results
    """
    cached_weight = cached_result["weight_per_fruit"] * cached_result["detected_count"]

    return JsonResponse(
        {
            "task_id": None,
            "status": "SUCCESS",
            "message": "Önbellekten döndürüldü",
            "from_cache": True,
            "result": {
                "detected_count": cached_result["detected_count"],
                "weight": cached_weight,
                "total_weight": agac_sayisi * cached_weight,
                "confidence_score": cached_result["confidence_score"],
                "image_path": cached_result["image_path"],
                "processing_time": 0.0,
            },
        },
        status=200,
    )


def _queue_detection_task(
    image_data: bytes,
    safe_filename: str,
    meyve_grubu: str,
    agac_sayisi: int,
    agac_yasi: int,
    user_id: int | None,
) -> JsonResponse:
    """
    Queue async detection task with Celery.

    Args:
        image_data: Raw image bytes
        safe_filename: Sanitized filename
        meyve_grubu: Fruit type
        agac_sayisi: Tree count
        agac_yasi: Tree age
        user_id: ID of authenticated user

    Returns:
        JsonResponse with task_id and status

    Raises:
        ValidationError: If file writing fails
    """
    from detection.tasks import process_image_detection

    temp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(temp_dir, safe_filename)

    try:
        with open(tmp_path, "wb") as tmp:
            tmp.write(image_data)
    except Exception as e:
        logger.error(f"Geçici dosya yazma hatası: {tmp_path}: {e}")
        raise ValidationError("Dosya yüklenirken hata oluştu")

    task = process_image_detection.delay(
        image_path=tmp_path,
        fruit_type=meyve_grubu,
        tree_count=agac_sayisi,
        tree_age=agac_yasi,
        user_id=user_id,
    )

    logger.info(f"Async detection task queued: {task.id} for {meyve_grubu}")

    return JsonResponse(
        {
            "task_id": task.id,
            "status": "PENDING",
            "message": "Görüntü işleme kuyruğa eklendi",
            "from_cache": False,
        },
        status=202,
    )


@login_required
@require_http_methods(["POST"])
def async_detection(request: HttpRequest) -> JsonResponse:
    """
    Asynchronous image detection endpoint using Celery.

    Returns task_id immediately while processing continues in background.
    """
    try:
        # Validate form inputs
        form_data = _validate_async_detection_form(request)
        filename = form_data["file"]

        # Prepare image data for caching
        safe_filename = sanitize_filename(filename.name or "")
        filename.seek(0)
        image_data = filename.read()
        filename.seek(0)

        # Calculate image hash for cache lookup
        image_hash = calculate_image_hash(image_data)

        # Check cache first
        cached_result = get_cached_prediction(image_hash, form_data["meyve_grubu"])

        if cached_result:
            # Cache HIT
            logger.info(
                f"Async endpoint: Using cached result for {form_data['meyve_grubu']}, hash={image_hash[:16]}..."
            )
            return _build_cached_async_response(cached_result, form_data["agac_sayisi"])

        # Cache MISS - queue async task
        return _queue_detection_task(
            image_data=image_data,
            safe_filename=safe_filename,
            meyve_grubu=form_data["meyve_grubu"],
            agac_sayisi=form_data["agac_sayisi"],
            agac_yasi=form_data["agac_yasi"],
            user_id=request.user.pk if request.user.is_authenticated else None,
        )

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Async detection hatası: {e}")
        return JsonResponse({"error": "Bir hata oluştu"}, status=500)


@login_required
@require_http_methods(["GET"])
def task_status(request: HttpRequest, task_id: str) -> JsonResponse:
    """
    Check status of a Celery task.

    URL Parameters:
        task_id: Celery task ID

    Returns:
        JSON: {
            'task_id': str,
            'status': str (PENDING, PROCESSING, SUCCESS, FAILURE),
            'result': dict (if SUCCESS),
            'error': str (if FAILURE),
            'progress': int (0-100)
        }
    """
    try:
        from celery.result import AsyncResult

        result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": result.state,
        }

        if result.state == "PENDING":
            response_data["message"] = "Görev bekleniyor..."
            response_data["progress"] = 0

        elif result.state == "PROCESSING":
            # Get custom meta information
            info = result.info or {}
            response_data["message"] = info.get("status", "İşleniyor...")
            response_data["progress"] = info.get("progress", 50)

        elif result.state == "SUCCESS":
            response_data["result"] = result.result
            response_data["message"] = "İşlem tamamlandı"
            response_data["progress"] = 100

        elif result.state == "FAILURE":
            # Get error information
            info = result.info or {}
            error_msg = str(result.info) if result.info else "Bilinmeyen hata"
            response_data["error"] = error_msg
            response_data["message"] = "İşlem başarısız"
            response_data["progress"] = 0

        else:
            # Other states (RETRY, REVOKED, etc.)
            response_data["message"] = f"Durum: {result.state}"
            response_data["progress"] = 0

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Task status check hatası: {e}")
        return JsonResponse(
            {
                "task_id": task_id,
                "error": "Görev durumu alınamadı",
                "status": "UNKNOWN",
            },
            status=500,
        )


@login_required
@require_http_methods(["POST", "DELETE"])
def cache_invalidate(request: HttpRequest) -> JsonResponse:
    """
    Invalidate cached predictions.

    POST/DELETE Parameters:
        - image_hash: (optional) SHA256 hash of specific image
        - fruit_type: (optional) Fruit type to invalidate
        - all: (optional) Set to 'true' to invalidate all predictions

    Returns:
        JSON: {
            'success': bool,
            'deleted_count': int,
            'message': str
        }
    """
    try:
        from detection.cache_utils import (
            invalidate_prediction_cache,
            invalidate_all_predictions,
        )

        # Get parameters from POST data or query params
        if request.method == "POST":
            image_hash = request.POST.get("image_hash")
            fruit_type = request.POST.get("fruit_type")
            invalidate_all = request.POST.get("all", "").lower() == "true"
        else:  # DELETE
            image_hash = request.GET.get("image_hash")
            fruit_type = request.GET.get("fruit_type")
            invalidate_all = request.GET.get("all", "").lower() == "true"

        if invalidate_all:
            # Invalidate all predictions (optionally filtered by fruit_type)
            deleted_count = invalidate_all_predictions(fruit_type=fruit_type)
            message = f"{deleted_count} önbellek anahtarı silindi"
            if fruit_type:
                message += f" ({fruit_type} için)"

            return JsonResponse(
                {"success": True, "deleted_count": deleted_count, "message": message}
            )

        elif image_hash and fruit_type:
            # Invalidate specific prediction
            success = invalidate_prediction_cache(image_hash, fruit_type)
            if success:
                return JsonResponse(
                    {
                        "success": True,
                        "deleted_count": 1,
                        "message": f"Önbellek anahtarı silindi: {fruit_type}, hash={image_hash[:16]}...",
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "deleted_count": 0,
                        "message": "Önbellek anahtarı bulunamadı",
                    },
                    status=404,
                )

        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Geçersiz parametreler. image_hash+fruit_type veya all=true gerekli",
                },
                status=400,
            )

    except Exception as e:
        logger.error(f"Cache invalidation hatası: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def cache_statistics(request: HttpRequest) -> JsonResponse:
    """
    Get cache statistics including hit/miss rates and memory usage.

    Returns:
        JSON: {
            'redis_available': bool,
            'prediction_keys_count': int,
            'prediction_memory_mb': float,
            'keyspace_hits': int,
            'keyspace_misses': int,
            'hit_rate_percent': float,
            'total_memory_used_mb': float,
            'total_memory_peak_mb': float,
            'connected_clients': int,
            'uptime_seconds': int
        }
    """
    try:
        from detection.cache_utils import get_cache_statistics

        stats = get_cache_statistics()

        return JsonResponse(stats)

    except Exception as e:
        logger.error(f"Cache statistics hatası: {e}")
        return JsonResponse({"redis_available": False, "error": str(e)}, status=500)
