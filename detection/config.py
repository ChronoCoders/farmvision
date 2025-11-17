# -*- coding: utf-8 -*-
"""
Shared configuration for fruit detection models and weights.

This module centralizes configuration used across the application to avoid
duplication and ensure consistency.
"""

# Fruit weight per unit in kilograms
FRUIT_WEIGHTS = {
    "mandalina": 0.125,  # Mandarin orange
    "elma": 0.105,       # Apple
    "armut": 0.220,      # Pear
    "seftale": 0.185,    # Peach
    "nar": 0.300,        # Pomegranate
}

# Model file mappings
FRUIT_MODELS = {
    "mandalina": "mandalina.pt",
    "elma": "elma.pt",
    "armut": "armut.pt",
    "seftale": "seftale.pt",
    "nar": "nar.pt",
}

# Tree detection model
TREE_MODEL = "agac.pt"

# Default detection parameters
DETECTION_DEFAULTS = {
    "img_size": 640,
    "conf_thres": 0.1,
    "iou_thres": 0.45,
}

# Validation ranges
VALIDATION_RANGES = {
    "tree_count": {"min": 1, "max": 100000},
    "tree_age": {"min": 0, "max": 150},
}


def get_fruit_weight(fruit_type: str) -> float:
    """
    Get the weight per unit for a given fruit type.

    Args:
        fruit_type: Type of fruit (e.g., 'mandalina', 'elma')

    Returns:
        Weight in kilograms per fruit unit

    Raises:
        KeyError: If fruit_type is not recognized
    """
    return FRUIT_WEIGHTS[fruit_type]


def get_model_path(fruit_type: str) -> str:
    """
    Get the model file path for a given fruit type.

    Args:
        fruit_type: Type of fruit (e.g., 'mandalina', 'elma')

    Returns:
        Model filename (e.g., 'mandalina.pt')

    Raises:
        KeyError: If fruit_type is not recognized
    """
    return FRUIT_MODELS[fruit_type]


def is_valid_fruit_type(fruit_type: str) -> bool:
    """
    Check if a fruit type is supported.

    Args:
        fruit_type: Type of fruit to validate

    Returns:
        True if supported, False otherwise
    """
    return fruit_type in FRUIT_MODELS


def validate_tree_count(count: int) -> bool:
    """
    Validate tree count is within acceptable range.

    Args:
        count: Number of trees

    Returns:
        True if valid, False otherwise
    """
    range_config = VALIDATION_RANGES["tree_count"]
    return range_config["min"] <= count <= range_config["max"]


def validate_tree_age(age: int) -> bool:
    """
    Validate tree age is within acceptable range.

    Args:
        age: Age of trees in years

    Returns:
        True if valid, False otherwise
    """
    range_config = VALIDATION_RANGES["tree_age"]
    return range_config["min"] <= age <= range_config["max"]
