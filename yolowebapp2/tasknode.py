# -*- coding: utf-8 -*-
import os
from pyodm import Node
import glob
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


class Node_processing:

    def __init__(self, image_dir):
        try:
            self.start_api = Node("localhost", 3000)
            self.task = self.create_node_task(image_folder=image_dir)
            self.uuid = self.task.uuid
        except Exception as e:
            logger.error(f"NodeODM connection error: {e}")
            raise ConnectionError(
                f"NodeODM'e bağlanılamadı. Docker çalışıyor mu? Hata: {e}"
            )

    def create_node_task(self, image_folder):
        try:
            images = glob.glob(f"{image_folder}/*.JPG") + glob.glob(
                f"{image_folder}/*.jpg"
            )

            if not images:
                raise ValueError(f"Klasörde JPG dosyası bulunamadı: {image_folder}")

            task = self.start_api.create_task(
                images, {"dsm": True, "dtm": True, "odm": True}
            )
            logger.info(f"Task oluşturuldu: {task.uuid}")
            return task
        except Exception as e:
            logger.error(f"Task oluşturma hatası: {e}")
            raise

    def download_task(self, path):
        try:
            logger.info(f"Task bekleniyor: {self.task.uuid}")
            self.task.wait_for_completion()

            os.makedirs(path, exist_ok=True)
            self.task.download_assets(path)
            logger.info(f"Sonuçlar indirildi: {path}")
        except Exception as e:
            logger.error(f"İndirme hatası: {e}")
            raise

    def get_uuid(self):
        return self.uuid

    def get_tasks(self, api):
        try:
            return self.start_api.get_task(api)
        except Exception as e:
            logger.error(f"Task bilgisi alınamadı: {e}")
            return None

    def task_info(self):
        try:
            info = self.start_api.info()
            return {
                "version": info.version,
                "task_queue_count": info.task_queue_count,
                "max_images": info.max_images,
                "engine_version": info.engine_version,
                "engine": info.engine,
            }
        except Exception as e:
            logger.error(f"Info alınamadı: {e}")
            return {}
