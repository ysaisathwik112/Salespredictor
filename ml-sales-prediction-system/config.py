"""
Application Configuration Module
Supports environment-based configuration (development, testing, production).
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration with shared settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "ml-sales-pred-secret-key-change-in-prod")
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'sales_prediction.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ML Artifacts
    MODEL_PATH = os.path.join(BASE_DIR, "ml", "artifacts", "model.pkl")
    SCALER_PATH = os.path.join(BASE_DIR, "ml", "artifacts", "scaler.pkl")
    ENCODER_PATH = os.path.join(BASE_DIR, "ml", "artifacts", "encoder.pkl")
    FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "ml", "artifacts", "feature_names.pkl")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-change-in-prod")
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    RATELIMIT_DEFAULT = "1000 per day;100 per hour"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
