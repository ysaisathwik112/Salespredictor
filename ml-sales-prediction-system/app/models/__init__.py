"""
Database Models
SQLAlchemy models for prediction history, user inputs, and logs.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class PredictionRecord(db.Model):
    """Stores prediction history for analytics and audit."""
    __tablename__ = "prediction_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # Input features
    item_weight = db.Column(db.Float, nullable=False)
    item_visibility = db.Column(db.Float, nullable=False)
    item_mrp = db.Column(db.Float, nullable=False)
    item_type = db.Column(db.String(64), nullable=False)
    outlet_size = db.Column(db.String(32), nullable=False)
    outlet_location_type = db.Column(db.String(32), nullable=False)
    outlet_type = db.Column(db.String(64), nullable=False)
    outlet_establishment_year = db.Column(db.Integer, nullable=False)

    # Prediction output
    predicted_sales = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)

    # Metadata
    model_version = db.Column(db.String(32), default="1.0.0")
    prediction_time_ms = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "input": {
                "item_weight": self.item_weight,
                "item_visibility": self.item_visibility,
                "item_mrp": self.item_mrp,
                "item_type": self.item_type,
                "outlet_size": self.outlet_size,
                "outlet_location_type": self.outlet_location_type,
                "outlet_type": self.outlet_type,
                "outlet_establishment_year": self.outlet_establishment_year,
            },
            "predicted_sales": self.predicted_sales,
            "confidence_score": self.confidence_score,
            "model_version": self.model_version,
            "prediction_time_ms": self.prediction_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class APILog(db.Model):
    """Stores API request/response logs for monitoring."""
    __tablename__ = "api_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    endpoint = db.Column(db.String(128), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time_ms = db.Column(db.Float, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": self.response_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelMetadata(db.Model):
    """Stores model version metadata for tracking and rollback."""
    __tablename__ = "model_metadata"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.String(32), unique=True, nullable=False)
    algorithm = db.Column(db.String(64), nullable=False)
    accuracy_r2 = db.Column(db.Float, nullable=True)
    rmse = db.Column(db.Float, nullable=True)
    mae = db.Column(db.Float, nullable=True)
    training_samples = db.Column(db.Integer, nullable=True)
    features_used = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    trained_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "algorithm": self.algorithm,
            "accuracy_r2": self.accuracy_r2,
            "rmse": self.rmse,
            "mae": self.mae,
            "training_samples": self.training_samples,
            "is_active": self.is_active,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
        }
