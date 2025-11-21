# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.db import transaction
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import os
import shutil

from .models import Projects
from .forms import Projects_Form
from yolowebapp2 import histogram as hs, hashing, tasknode, options, predict_tree

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)

HEALTH_ALGORITHMS = {
    "ndvi": "Ndvi",
    "gli": "Gli",
    "vari": "Vari",
    "vndvi": "VNDVI",
    "ndyi": "NDYI",
    "ndre": "NDRE",
    "ndwi": "NDWI",
    "ndvi_blue": "NDVI_Blue",
    "endvi": "ENDVI",
    "mpri": "MPRI",
    "exg": "EXG",
    "tgi": "TGI",
    "bai": "BAI",
    "gndvi": "GNDVI",
    "grvi": "GRVI",
    "savi": "SAVI",
    "mnli": "MNLI",
    "msr": "MSR",
    "rdvi": "RDVI",
    "tdvi": "TDVI",
    "osavi": "OSAVI",
    "lai": "LAI",
    "evi": "EVI",
    "arvi": "ARVI",
}

MAX_FILE_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "tif", "tiff"}


def validate_uploaded_files(files: List[Any]) -> None:
    if not files:
        raise ValidationError("Dosya bulunamadı")

    for file in files:
        if not file:
            raise ValidationError("Geçersiz dosya")

        if file.size > MAX_FILE_SIZE:
            raise ValidationError(f"Dosya çok büyük: {file.name}")

        if file.size == 0:
            raise ValidationError(f"Boş dosya: {file.name}")

        # Extract basename to prevent path traversal
        filename = os.path.basename(file.name)

        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            logger.warning(f"Path traversal attempt detected: {file.name}")
            raise ValidationError(f"Geçersiz dosya adı: {file.name}")

        ext = filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(f"Geçersiz dosya tipi: {ext}")


def task_path(id: str, path: str, file: str) -> str:
    return f"results/{id}/{path}/{file}"


def get_full_task_path(id: str, path: str, file: str) -> str:
    return os.path.join(BASE_DIR, f"static/results/{id}/{path}", file)


def get_statistics(id: str, type: str) -> Dict[str, Any]:
    if type == "static":
        task = get_full_task_path(id, "odm_report", "stats.json")

        if os.path.isfile(task):
            try:
                import json

                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:
                return {"error": str(e)}
            return {
                "gsd": j.get("odm_processing_statistics", {}).get("average_gsd"),
                "area": j.get("processing_statistics", {}).get("area"),
                "date": j.get("processing_statistics", {}).get("date"),
                "end_date": j.get("processing_statistics", {}).get("end_date"),
            }
        else:
            return {}

    elif type == "orthophoto" or type == "plant":
        task = task_path(id, "odm_orthophoto", "odm_orthophoto.tif")
        return {"odm_orthophoto": task}

    elif type == "dsm":
        task = task_path(id, "odm_dem", "dsm.tif")
        return {"dsm": task}

    elif type == "dtm":
        task = task_path(id, "odm_dem", "dtm.tif")
        return {"dtm": task}

    elif type == "camera_shots":
        task = task_path(id, "odm_report", "shots.geojson")
        if os.path.isfile(task):
            try:
                import json

                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:
                return {"error": str(e)}
            return {"camera_shots": j}
        else:
            return {}

    elif type == "images_info":
        task = get_full_task_path(id, "/", "images.json")

        if os.path.exists(task):
            try:
                import json

                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:
                return {"error": str(e)}
            return {
                "camera_model": j[0].get("camera_model"),
                "altitude": j[0].get("altitude"),
            }
        else:
            return {}

    return {}


@login_required
def projects(request: HttpRequest) -> HttpResponse:
    projes = Projects.objects.all()
    return render(request, "projects.html", {"projes": projes, "userss": request.user})


@login_required
def add_projects(
    request: HttpRequest, slug: Optional[str] = None, id: Optional[int] = None
) -> HttpResponse:
    if slug == "update" and id:
        if not hasattr(request.user, "is_staff") or not request.user.is_staff:
            raise PermissionDenied("Güncelleme yetkisi yok")

        projes = get_object_or_404(Projects, id=id)

        if request.method == "POST":
            try:
                form = Projects_Form(
                    request.POST, request.FILES, instance=projes)
                if form.is_valid():
                    try:
                        with transaction.atomic():
                            form.save()
                        logger.info(f"Proje güncellendi: {projes.id}")
                        return redirect("dron_map:projects")
                    except Exception as e:
                        logger.error(f"Veritabanı güncelleme hatası: {e}")
                        return render(
                            request,
                            "add-projects.html",
                            {
                                "projes": projes,
                                "error": "Proje güncellenemedi",
                                "userss": request.user,
                            },
                        )
                return render(
                    request,
                    "add-projects.html",
                    {"projes": projes, "errors": form.errors, "userss": request.user},
                )
            except Exception as e:
                logger.error(f"Update error: {e}")
                return render(
                    request,
                    "add-projects.html",
                    {
                        "projes": projes,
                        "error": "Güncelleme hatası",
                        "userss": request.user,
                    },
                )

        return render(
            request, "add-projects.html", {"projes": projes,
                                           "userss": request.user}
        )

    elif slug == "delete" and id:
        if not hasattr(request.user, "is_staff") or not request.user.is_staff:
            raise PermissionDenied("Silme yetkisi yok")

        projes = get_object_or_404(Projects, id=id)

        try:
            project_id = projes.id
            with transaction.atomic():
                projes.delete()
            logger.info(f"Proje silindi: {project_id}")
            return redirect("dron_map:projects")
        except Exception as e:
            logger.error(f"Proje silme hatası: {id}: {e}")
            return render(
                request,
                "add-projects.html",
                {"projes": projes, "error": "Proje silinemedi",
                    "userss": request.user},
            )

    elif slug == "add":
        if request.method == "POST":
            try:
                form = Projects_Form(request.POST, request.FILES)

                if not form.is_valid():
                    return render(
                        request,
                        "add-projects.html",
                        {"errors": form.errors, "userss": request.user},
                    )

                images_list = request.FILES.getlist("picture")
                validate_uploaded_files(images_list)

                title = form.cleaned_data["Title"]
                field = form.cleaned_data["Field"]

                # Create hashing path
                try:
                    hass = hashing.add_prefix(filename=f"{title}{field}")
                    upload_dir = Path(hass[0])
                except Exception as e:
                    logger.error(f"Hashing path oluşturma hatası: {e}")
                    raise ValidationError("Proje dizini oluşturulamadı")

                # Save uploaded images
                saved_files_dir = None
                try:
                    for image in images_list:
                        # Sanitize filename to prevent path traversal
                        if image.name is None:
                            raise ValidationError("Dosya adı bulunamadı")

                        safe_filename = os.path.basename(image.name)
                        if (
                            ".." in safe_filename
                            or "/" in safe_filename
                            or "\\" in safe_filename
                        ):
                            logger.warning(
                                f"Path traversal attempt in filename: {image.name}"
                            )
                            raise ValidationError(
                                f"Geçersiz dosya adı: {image.name}")

                        fs = FileSystemStorage(location=str(hass[0]))
                        saved_path = fs.save(safe_filename, image)
                        if not saved_path:
                            logger.error(
                                f"Dosya kaydetme başarısız: {safe_filename}")
                            raise IOError(
                                f"Dosya kaydedilemedi: {safe_filename}")
                    saved_files_dir = upload_dir
                except Exception as e:
                    logger.error(f"Görüntü kaydetme hatası: {e}")
                    # Clean up any files that were saved
                    if upload_dir.exists():
                        try:
                            shutil.rmtree(str(upload_dir))
                            logger.info(
                                f"Hatalı dosyalar temizlendi: {upload_dir}")
                        except Exception as cleanup_error:
                            logger.error(
                                f"Dosya temizleme hatası: {cleanup_error}")
                    raise ValidationError(f"Dosyalar kaydedilemedi: {str(e)}")

                # Save project to database with transaction
                try:
                    with transaction.atomic():
                        form.instance.hashing_path = hass[1]
                        project = form.save()
                        logger.info(
                            f"Proje veritabanına kaydedildi: {project.id}")
                except Exception as e:
                    logger.error(f"Veritabanı kaydetme hatası: {e}")
                    # Database save failed, clean up saved files
                    if saved_files_dir and saved_files_dir.exists():
                        try:
                            shutil.rmtree(str(saved_files_dir))
                            logger.info(
                                f"Veritabanı hatası nedeniyle dosyalar silindi: {saved_files_dir}"
                            )
                        except Exception as cleanup_error:
                            logger.error(
                                f"Dosya temizleme hatası: {cleanup_error}")
                    raise ValidationError("Proje kaydedilemedi")

                # Process task (non-critical, log but don't fail)
                try:
                    p = tasknode.Node_processing(str(hass[0]))
                    p.download_task(f"{BASE_DIR}/static/results/{hass[1]}")
                except Exception as e:
                    logger.error(f"Task processing error: {e}")
                    # Don't raise, just log - this is not critical

                return redirect("dron_map:projects")

            except ValidationError as e:
                return render(
                    request,
                    "add-projects.html",
                    {"error": str(e), "userss": request.user},
                )
            except Exception as e:
                logger.error(f"Add project error: {e}")
                return render(
                    request,
                    "add-projects.html",
                    {"error": "Proje oluşturulamadı", "userss": request.user},
                )

        return render(request, "add-projects.html", {"userss": request.user})

    # Default case: if no slug matches, redirect to projects list
    return redirect("dron_map:projects")


def convert(input_path: str, output_path: str) -> None:
    try:
        from osgeo import gdal

        dataset1 = gdal.Open(input_path)
        if dataset1 is None:
            error_msg = f"GDAL: Kaynak dosya açılamadı: {input_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        projection = dataset1.GetProjection()
        geotransform = dataset1.GetGeoTransform()

        dataset2 = gdal.Open(output_path, gdal.GA_Update)
        if dataset2 is None:
            error_msg = f"GDAL: Hedef dosya açılamadı: {output_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        dataset2.SetGeoTransform(geotransform)
        dataset2.SetProjection(projection)
        dataset2.GetRasterBand(1).SetNoDataValue(0)

        # Close datasets
        dataset1 = None
        dataset2 = None

    except ImportError as e:
        error_msg = f"GDAL kütüphanesi yüklenemedi: {e}"
        logger.error(error_msg)
        raise ImportError(error_msg)
    except AttributeError as e:
        error_msg = f"GDAL dataset hatalı: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"GDAL dönüştürme hatası: {e}"
        logger.error(error_msg)
        raise


@login_required
def maping(request: HttpRequest, id: int) -> HttpResponse:
    projes = get_object_or_404(Projects, id=id)
    algo = options.algorithm
    colors = options.colormaps

    if request.method == "POST":
        orthophoto = get_statistics(id=projes.hashing_path, type="orthophoto")
        static = get_statistics(id=projes.hashing_path, type="static")
        images_info = get_statistics(
            id=projes.hashing_path, type="images_info")

        try:
            range_values = request.POST.getlist("range")
            post_range = tuple(float(v) for v in range_values[:2])
            post_range = (-abs(post_range[0]), abs(post_range[1]))
        except (ValueError, IndexError, TypeError):
            return render(
                request,
                "map.html",
                {
                    "projes": projes,
                    "orthophoto": orthophoto,
                    "algo": options.algorithm,
                    "colors": options.colormaps,
                    "static": static,
                    "images_info": images_info,
                    "error": "Geçersiz aralık değeri",
                },
            )

        health_color = request.POST.get("health_color", "")
        cmap = request.POST.get("cmap", "")

        if health_color == "detect":
            try:
                detec, unique_id, _ = predict_tree.predict(
                    path_to_weights="agac.pt",
                    path_to_source=f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',
                )
                convert(
                    f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',
                    f"{BASE_DIR}/static/detected/{unique_id}/odm_orthophoto.tif",
                )
                return render(
                    request,
                    "map.html",
                    {
                        "orthophoto": {
                            "path": f"detected/{unique_id}/odm_orthophoto.tif",
                            "colormap": cmap,
                            "ranges": post_range,
                        },
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                        "detection": detec.decode("utf-8"),
                    },
                )
            except (ValueError, ImportError) as e:
                logger.error(f"Detection conversion error: {e}")
                return render(
                    request,
                    "map.html",
                    {
                        "projes": projes,
                        "orthophoto": orthophoto,
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                        "error": "Algılama veya dönüştürme hatası",
                    },
                )
            except Exception as e:
                logger.error(f"Unexpected detection error: {e}")
                return render(
                    request,
                    "map.html",
                    {
                        "projes": projes,
                        "orthophoto": orthophoto,
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                        "error": "Beklenmeyen bir hata oluştu",
                    },
                )

        elif health_color in HEALTH_ALGORITHMS:
            try:
                orthophoto_path = f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}'

                # Check if file exists
                if not os.path.exists(orthophoto_path):
                    logger.error(f"Orthophoto bulunamadı: {orthophoto_path}")
                    return render(
                        request,
                        "map.html",
                        {
                            "projes": projes,
                            "orthophoto": orthophoto,
                            "algo": algo,
                            "colors": colors,
                            "static": static,
                            "images_info": images_info,
                            "error": "Orthophoto dosyası bulunamadı",
                        },
                    )

                a = hs.algos(orthophoto_path, projes.hashing_path)
                method = getattr(a, HEALTH_ALGORITHMS[health_color])
                result = method(post_range, cmap)
                return render(
                    request,
                    "map.html",
                    {
                        "orthophoto": result,
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                    },
                )

            except AttributeError as e:
                logger.error(
                    f"Algoritma metodu bulunamadı: {health_color}: {e}")
                return render(
                    request,
                    "map.html",
                    {
                        "projes": projes,
                        "orthophoto": orthophoto,
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                        "error": "Algoritma bulunamadı",
                    },
                )
            except Exception as e:
                logger.error(f"Sağlık algoritması hatası: {health_color}: {e}")
                return render(
                    request,
                    "map.html",
                    {
                        "projes": projes,
                        "orthophoto": orthophoto,
                        "algo": algo,
                        "colors": colors,
                        "static": static,
                        "images_info": images_info,
                        "error": "Algoritma işleme hatası",
                    },
                )

        # Default return for POST if no health_color action matched
        return render(
            request,
            "map.html",
            {
                "projes": projes,
                "orthophoto": orthophoto,
                "algo": algo,
                "colors": colors,
                "static": static,
                "images_info": images_info,
            },
        )
    else:
        orthophoto = get_statistics(id=projes.hashing_path, type="orthophoto")
        static = get_statistics(id=projes.hashing_path, type="static")
        images_info = get_statistics(
            id=projes.hashing_path, type="images_info")

        return render(
            request,
            "map.html",
            {
                "projes": projes,
                "orthophoto": orthophoto,
                "algo": algo,
                "colors": colors,
                "static": static,
                "images_info": images_info,
            },
        )
