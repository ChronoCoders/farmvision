# -*- coding: utf-8 -*-
from django.apps import AppConfig
import os


class DetectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "detection"

    def ready(self):
        # Django reloader içinde mi kontrol et
        if os.environ.get("RUN_MAIN") != "true":
            return

        # Models will be loaded lazily on first use to avoid slow startup
        print("Detection app ready. Models will load on first use.")
