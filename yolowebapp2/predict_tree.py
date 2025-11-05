# -*- coding: utf-8 -*-
from pathlib import Path
import openpyxl
from natsort import natsorted
import numpy as np
import glob
import zipfile
import torch
import cv2
import sys
import threading
import uuid
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR / "detection" / "yolo"))
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device
from utils.datasets import LoadImages

_model_cache = {}
_device = None
_lock = threading.RLock()


def get_device() -> torch.device:
    global _device
    with _lock:
        if _device is None:
            try:
                _device = select_device("")
                logger.info(f"Device seçildi: {_device}")
            except Exception as e:
                logger.error(f"Device seçim hatası: {e}")
                raise RuntimeError(f"GPU/CPU seçimi başarısız: {e}")
        return _device


def get_model(model_name: str) -> Any:
    with _lock:
        if model_name not in _model_cache:
            try:
                device = get_device()
                model_path = BASE_DIR / "detection" / "yolo" / model_name

                if not model_path.exists():
                    logger.error(f"Model dosyası bulunamadı: {model_path}")
                    raise FileNotFoundError(f"Model bulunamadı: {model_path}")

                logger.info(f"Model yükleniyor: {model_name}")
                model = attempt_load(str(model_path), map_location=device)
                model.eval()

                if device.type != "cpu":
                    model.half()

                _model_cache[model_name] = model
                logger.info(f"Model başarıyla yüklendi: {model_name}")

            except FileNotFoundError:
                raise
            except Exception as e:
                logger.error(f"Model yükleme hatası {model_name}: {e}")
                raise RuntimeError(f"Model yüklenemedi {model_name}: {e}")

        return _model_cache[model_name]


def preddict(path_to_weights: str, path_to_source: str) -> Tuple[bytes, str, float]:
    unique_id = str(uuid.uuid4())

    try:
        model = get_model(path_to_weights)
        device = get_device()

        img_size = 640
        conf_thres = 0.1
        iou_thres = 0.45

        try:
            dataset = LoadImages(path_to_source, img_size=img_size)
        except Exception as e:
            logger.error(f"Görüntü yükleme hatası: {path_to_source}: {e}")
            raise ValueError(f"Görüntü yüklenemedi: {e}")

        total_detections = 0
        confidence_scores = []

        for path, img, im0s, vid_cap in dataset:
            try:
                img = torch.from_numpy(img).to(device)
                img = img.half() if device.type != "cpu" else img.float()
                img /= 255.0

                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                with torch.no_grad():
                    pred = model(img)[0]

                pred = non_max_suppression(pred, conf_thres, iou_thres)

                for i, det in enumerate(pred):
                    im0 = im0s.copy()

                    if len(det):
                        det[:, :4] = scale_coords(
                            img.shape[2:], det[:, :4], im0.shape
                        ).round()
                        total_detections = len(det)

                        from numpy import random

                        colors = [[random.randint(0, 255) for _ in range(3)]]

                        for *xyxy, conf, cls in reversed(det):
                            confidence_scores.append(float(conf))
                            label = f"{conf:.2f}"
                            plot_one_box(
                                xyxy,
                                im0,
                                label=label,
                                color=colors[0],
                                line_thickness=2,
                            )

                    try:
                        output_dir = BASE_DIR / "static" / "detected" / unique_id
                        output_dir.mkdir(parents=True, exist_ok=True)

                        img_name = Path(path).name
                        output_path = output_dir / img_name

                        if not cv2.imwrite(str(output_path), im0):
                            logger.error(f"Görüntü yazma hatası: {output_path}")
                            raise IOError(f"Görüntü kaydedilemedi: {output_path}")

                    except Exception as e:
                        logger.error(f"Çıktı dosyası yazma hatası: {e}")
                        raise IOError(f"Sonuç görüntüsü kaydedilemedi: {e}")

            except Exception as e:
                logger.error(f"Algılama işlemi hatası: {path}: {e}")
                raise

        count_str = f"{total_detections:02d}"
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )
        return count_str.encode("utf-8"), unique_id, avg_confidence

    except (FileNotFoundError, RuntimeError, ValueError, IOError):
        raise
    except Exception as e:
        logger.error(f"Preddict genel hatası: {e}")
        raise RuntimeError(f"Algılama işlemi başarısız: {e}")


def multi_predictor(
    path_to_weights: str, path_to_source: str, ekim_sirasi: str, hashing: str
) -> str:
    try:
        try:
            a_str, b_str = ekim_sirasi.split("-")
            a: int = int(a_str)
            b: int = int(b_str)
        except (ValueError, AttributeError) as e:
            logger.error(f"Ekim sırası parse hatası: {ekim_sirasi}: {e}")
            raise ValueError(f"Geçersiz ekim sırası formatı: {ekim_sirasi}")

        try:
            path_to_source_images = natsorted(glob.glob(f"{path_to_source}/*"))
            if not path_to_source_images:
                logger.error(f"Kaynak dizinde görüntü bulunamadı: {path_to_source}")
                raise FileNotFoundError(f"Görüntü bulunamadı: {path_to_source}")
        except Exception as e:
            logger.error(f"Görüntü listesi oluşturma hatası: {e}")
            raise

        model = get_model(path_to_weights)
        device = get_device()

        img_size = 640
        conf_thres = 0.1
        iou_thres = 0.45

        detection_counts = []

        try:
            output_dir = Path(path_to_source) / "detected"
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Çıktı dizini oluşturma hatası: {e}")
            raise IOError(f"Dizin oluşturulamadı: {e}")

        for img_path in path_to_source_images:
            try:
                dataset = LoadImages(img_path, img_size=img_size)

                for path, img, im0s, vid_cap in dataset:
                    img = torch.from_numpy(img).to(device)
                    img = img.half() if device.type != "cpu" else img.float()
                    img /= 255.0

                    if img.ndimension() == 3:
                        img = img.unsqueeze(0)

                    with torch.no_grad():
                        pred = model(img)[0]

                    pred = non_max_suppression(pred, conf_thres, iou_thres)

                    total_detections = 0
                    for i, det in enumerate(pred):
                        im0 = im0s.copy()

                        if len(det):
                            det[:, :4] = scale_coords(
                                img.shape[2:], det[:, :4], im0.shape
                            ).round()
                            total_detections = len(det)

                            from numpy import random

                            colors = [[random.randint(0, 255) for _ in range(3)]]

                            for *xyxy, conf, cls in reversed(det):
                                label = f"{conf:.2f}"
                                plot_one_box(
                                    xyxy,
                                    im0,
                                    label=label,
                                    color=colors[0],
                                    line_thickness=2,
                                )

                        img_name = Path(path).name
                        output_path = output_dir / img_name
                        if not cv2.imwrite(str(output_path), im0):
                            logger.error(f"Görüntü kaydetme hatası: {output_path}")

                    detection_counts.append(total_detections)

            except Exception as e:
                logger.error(f"Görüntü işleme hatası {img_path}: {e}")
                detection_counts.append(0)

        try:
            excel_dir = Path(path_to_source) / "excel"
            excel_dir.mkdir(parents=True, exist_ok=True)

            expected_size = a * b
            actual_size = len(detection_counts)
            if expected_size != actual_size:
                logger.error(
                    f"Reshape boyut uyumsuzluğu: beklenen {expected_size} "
                    f"({a}x{b}), gerçek {actual_size}"
                )
                raise ValueError(
                    f"Ekim sırası ({a}x{b}={expected_size}) ile görüntü sayısı "
                    f"({actual_size}) uyuşmuyor. Lütfen doğru ekim sırası giriniz."
                )

            data = np.array(detection_counts).reshape(a, b)
            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                raise IOError("Excel worksheet oluşturulamadı")
            for row in data:
                ws.append([int(x) for x in row])

            excel_path = excel_dir / "output.xlsx"
            wb.save(str(excel_path))
            logger.info(f"Excel dosyası oluşturuldu: {excel_path}")

        except Exception as e:
            logger.error(f"Excel oluşturma hatası: {e}")
            raise IOError(f"Excel dosyası oluşturulamadı: {e}")

        try:
            zip_path = BASE_DIR / "media" / f"{hashing}_result.zip"
            zip_path.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(
                str(zip_path), mode="w", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                archive.write(str(excel_dir / "output.xlsx"), "output.xlsx")
                for img in natsorted(output_dir.glob("*")):
                    archive.write(str(img), f"detected/{img.name}")

            logger.info(f"ZIP dosyası oluşturuldu: {zip_path}")

        except Exception as e:
            logger.error(f"ZIP oluşturma hatası: {e}")
            raise IOError(f"ZIP dosyası oluşturulamadı: {e}")

        return hashing

    except (FileNotFoundError, ValueError, IOError, RuntimeError):
        raise
    except Exception as e:
        logger.error(f"Multi predictor genel hatası: {e}")
        raise RuntimeError(f"Çoklu algılama işlemi başarısız: {e}")


def tree_detection(img_path: str) -> Dict[str, Any]:
    unique_id = str(uuid.uuid4())

    try:
        from PIL import Image
        from PIL.Image import Image as ImageType

        try:
            im: ImageType = Image.open(img_path)
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
        except Exception as e:
            logger.error(f"PIL görüntü açma hatası: {img_path}: {e}")
            raise ValueError(f"Görüntü açılamadı: {e}")

        try:
            convertor_dir = BASE_DIR / "static" / "convertor"
            convertor_dir.mkdir(parents=True, exist_ok=True)
            convert_path = convertor_dir / "convert.jpeg"
            im.save(str(convert_path))
        except Exception as e:
            logger.error(f"Görüntü kaydetme hatası: {convert_path}: {e}")
            raise IOError(f"Geçici görüntü kaydedilemedi: {e}")

        model = get_model("agac.pt")
        device = get_device()

        img_size = 640
        conf_thres = 0.25
        iou_thres = 0.7

        try:
            dataset = LoadImages(str(convert_path), img_size=img_size)
        except Exception as e:
            logger.error(f"Dataset yükleme hatası: {e}")
            raise ValueError(f"Dataset yüklenemedi: {e}")

        results_dict: Dict[str, Any] = {}

        for path, img, im0s, vid_cap in dataset:
            try:
                img = torch.from_numpy(img).to(device)
                img = img.half() if device.type != "cpu" else img.float()
                img /= 255.0

                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                with torch.no_grad():
                    pred = model(img)[0]

                pred = non_max_suppression(pred, conf_thres, iou_thres)

                for i, det in enumerate(pred):
                    im0 = im0s.copy()

                    if len(det):
                        det[:, :4] = scale_coords(
                            img.shape[2:], det[:, :4], im0.shape
                        ).round()

                        for *xyxy, conf, cls in reversed(det):
                            results_dict["class_name"] = "agac"
                            results_dict["confidence"] = float(conf)
                            break
                        break

                try:
                    output_dir = BASE_DIR / "static" / "detected" / unique_id
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / "detection.jpg"

                    if not cv2.imwrite(str(output_path), im0):
                        logger.error(f"Algılama görüntüsü yazma hatası: {output_path}")
                        raise IOError("Sonuç görüntüsü kaydedilemedi")

                except Exception as e:
                    logger.error(f"Çıktı kaydetme hatası: {e}")
                    raise IOError(f"Sonuç kaydedilemedi: {e}")

            except Exception as e:
                logger.error(f"Ağaç algılama işlemi hatası: {e}")
                raise

        return {"name": results_dict.get("class_name"), "unique_id": unique_id}

    except (FileNotFoundError, ValueError, IOError, RuntimeError):
        raise
    except Exception as e:
        logger.error(f"Tree detection genel hatası: {e}")
        raise RuntimeError(f"Ağaç algılama başarısız: {e}")


def preload_all_models() -> None:
    models = ["mandalina.pt", "elma.pt", "armut.pt", "seftale.pt", "nar.pt", "agac.pt"]
    loaded_count = 0

    for model_name in models:
        try:
            model_path = BASE_DIR / "detection" / "yolo" / model_name
            if model_path.exists():
                get_model(model_name)
                loaded_count += 1
            else:
                print(f"Model bulunamadı: {model_name}")
        except Exception as e:
            print(f"Model yükleme hatası {model_name}: {e}")

    print(f"{loaded_count}/{len(models)} model yüklendi")
