# -*- coding: utf-8 -*-
"""
Model Registry for tracking ML model versions and metadata
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Model metadata registry
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "mandalina.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.92,
        "description": "Mandalina meyve algılama modeli",
        "training_dataset_size": 5000,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.1,
        "iou_threshold": 0.45,
    },
    "elma.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.89,
        "description": "Elma meyve algılama modeli",
        "training_dataset_size": 4800,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.1,
        "iou_threshold": 0.45,
    },
    "armut.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.88,
        "description": "Armut meyve algılama modeli",
        "training_dataset_size": 4500,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.1,
        "iou_threshold": 0.45,
    },
    "seftale.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.90,
        "description": "Şeftali meyve algılama modeli",
        "training_dataset_size": 4600,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.1,
        "iou_threshold": 0.45,
    },
    "nar.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.91,
        "description": "Nar meyve algılama modeli",
        "training_dataset_size": 4700,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.1,
        "iou_threshold": 0.45,
    },
    "agac.pt": {
        "version": "1.0.0",
        "date": datetime(2024, 1, 15),
        "accuracy": 0.87,
        "description": "Ağaç algılama modeli",
        "training_dataset_size": 3500,
        "framework": "YOLOv5",
        "input_size": 640,
        "confidence_threshold": 0.25,
        "iou_threshold": 0.7,
    },
}


def get_model_info(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific model

    Args:
        model_name: Name of the model file (e.g., 'mandalina.pt')

    Returns:
        Dictionary with model metadata or None if model not found
    """
    return MODEL_REGISTRY.get(model_name)


def get_all_models() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata for all registered models

    Returns:
        Dictionary mapping model names to their metadata
    """
    return MODEL_REGISTRY.copy()


def get_model_version(model_name: str) -> Optional[str]:
    """
    Get version string for a specific model

    Args:
        model_name: Name of the model file

    Returns:
        Version string or None if model not found
    """
    model_info = get_model_info(model_name)
    return model_info.get("version") if model_info else None


def get_model_accuracy(model_name: str) -> Optional[float]:
    """
    Get accuracy score for a specific model

    Args:
        model_name: Name of the model file

    Returns:
        Accuracy as float between 0 and 1, or None if model not found
    """
    model_info = get_model_info(model_name)
    return model_info.get("accuracy") if model_info else None


def register_model(model_name: str, metadata: Dict[str, Any]) -> None:
    """
    Register a new model or update existing model metadata

    Args:
        model_name: Name of the model file
        metadata: Dictionary containing model metadata
    """
    required_fields = ["version", "date", "accuracy", "description"]

    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field: {field}")

    MODEL_REGISTRY[model_name] = metadata
    logger.info(f"Model registered: {model_name} v{metadata['version']}")


def get_loaded_models_info() -> list:
    """
    Get information about all loaded/registered models

    Returns:
        List of dictionaries containing model information with model_id and is_loaded status
    """
    loaded_models = []
    for model_name, info in MODEL_REGISTRY.items():
        loaded_models.append(
            {
                "model_id": model_name,
                "is_loaded": True,
                "version": info["version"],
                "date": info["date"].strftime("%Y-%m-%d"),
                "accuracy": info["accuracy"],
                "description": info["description"],
                "framework": info.get("framework", "Unknown"),
                "input_size": info.get("input_size", 0),
            }
        )
    return loaded_models


def log_registry_info() -> None:
    """
    Log information about all registered models
    """
    logger.info("=" * 70)
    logger.info("Model Registry Information")
    logger.info("=" * 70)

    for model_name, info in MODEL_REGISTRY.items():
        logger.info("Model: %s", model_name)
        logger.info(f"  Version: {info['version']}")
        logger.info(f"  Date: {info['date'].strftime('%Y-%m-%d')}")
        logger.info(f"  Accuracy: {info['accuracy']:.2%}")
        logger.info(f"  Description: {info['description']}")
        logger.info("-" * 70)

    logger.info("Total models registered: %s", len(MODEL_REGISTRY))
    logger.info("=" * 70)


# Initialize registry on import
try:
    log_registry_info()
except Exception as e:
    logger.error("Failed to log registry info: %s", e)
