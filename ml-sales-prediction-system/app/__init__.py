"""
Flask Application Factory
Creates and configures the Flask application with all extensions and blueprints.
"""

import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from config import get_config


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"),
        static_url_path="/static",
    )

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
    }
    swagger_template = {
        "info": {
            "title": "Sales Prediction API",
            "description": "Enterprise-grade ML-powered Sales Prediction REST API",
            "version": "1.0.0",
            "contact": {"name": "API Support"},
        },
        "basePath": "/",
        "schemes": ["http", "https"],
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Ensure instance and log directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config.get("LOG_DIR", "logs"), exist_ok=True)

    # Initialize logging
    from app.utils.logger import setup_logging
    setup_logging(app)

    # Initialize database
    from app.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Load ML model at startup
    from app.services.prediction_service import PredictionService
    with app.app_context():
        PredictionService.load_model(app)

    app.logger.info("Sales Prediction Application initialized successfully")

    return app
