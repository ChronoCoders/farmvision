# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Use project root for logs directory
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "analysis_logs.json"


def _ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_latest_analysis_data(project_id: int) -> dict:
    """Return the most recent analysis log entry for a given project_id."""
    _ensure_logs_dir()

    if not LOG_FILE.exists():
        return {}

    latest = None
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("project_id") == project_id:
                    latest = entry
            except json.JSONDecodeError:
                continue

    return latest or {}


def log_full_analysis(
    project_id: int,
    raster_path: str,
    start_time: datetime,
    end_time: datetime,
    ndvi_low: float,
    ndvi_high: float,
    min_area_ha: float,
    grid_size: float,
    yield_model_version: str,
    success: bool,
    error_message: str | None = None,
    stack_trace: str | None = None,
) -> None:
    _ensure_logs_dir()

    duration = (end_time - start_time).total_seconds()

    entry: dict[str, Any] = {
        "project_id": project_id,
        "raster_path": raster_path,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "ndvi_low": ndvi_low,
        "ndvi_high": ndvi_high,
        "min_area_ha": min_area_ha,
        "grid_size": grid_size,
        "yield_model_version": yield_model_version,
        "success": success,
        "error_message": error_message or "",
        "stack_trace": stack_trace or "",
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")


def get_latest_analysis_data(project_id: int) -> dict:
    """
    Retrieves the latest analysis data for a given project_id.
    This function reads from the log file (simulated DB) and returns a mock analysis structure
    suitable for report generation, as the log file might not contain all detailed results.
    In a real scenario, this would query a proper database or load a detailed result file.
    """
    # Mock return for now since the logs only store metadata
    # In production, fetch real analysis results associated with the project
    return {
        "summary": {
            "total_area": 150.5,
            "stressed_area": 45.2,
            "healthy_area": 105.3,
            "average_ndvi": 0.65
        },
        "stress_zones": [
            {"id": 1, "severity": "high", "area": 10.5, "recommendation": "Check irrigation"},
            {"id": 2, "severity": "medium", "area": 34.7, "recommendation": "Monitor soil moisture"}
        ]
    }
