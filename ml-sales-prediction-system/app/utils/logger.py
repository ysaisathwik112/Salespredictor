"""
Logging Utility
Configures structured logging with file rotation and colored console output.
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure application logging with file and console handlers."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    log_dir = app.config.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()
    app.logger.handlers.clear()

    # Log format
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # File handler - Application logs
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(file_format)

    # File handler - Error logs
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)

    # File handler - Prediction logs
    prediction_handler = RotatingFileHandler(
        os.path.join(log_dir, "predictions.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    prediction_handler.setLevel(logging.INFO)
    prediction_handler.setFormatter(file_format)
    prediction_logger = logging.getLogger("predictions")
    prediction_logger.addHandler(prediction_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_format)

    # Add handlers
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    app.logger.info("Logging configured [level=%s, dir=%s]", app.config.get("LOG_LEVEL"), log_dir)
