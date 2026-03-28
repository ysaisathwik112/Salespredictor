"""
Prediction Service
Handles model loading, preprocessing, and prediction logic.
"""

import os
import time
import logging
import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
prediction_logger = logging.getLogger("predictions")


class PredictionService:
    """Service for managing ML model and making predictions."""

    _model = None
    _scaler = None
    _encoder = None
    _feature_names = None
    _model_version = "1.0.0"
    _is_loaded = False

    @classmethod
    def load_model(cls, app=None):
        """Load ML model, scaler, and encoder from artifacts."""
        try:
            if app:
                model_path = app.config.get("MODEL_PATH")
                scaler_path = app.config.get("SCALER_PATH")
                encoder_path = app.config.get("ENCODER_PATH")
                feature_names_path = app.config.get("FEATURE_NAMES_PATH")
            else:
                base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml", "artifacts")
                model_path = os.path.join(base, "model.pkl")
                scaler_path = os.path.join(base, "scaler.pkl")
                encoder_path = os.path.join(base, "encoder.pkl")
                feature_names_path = os.path.join(base, "feature_names.pkl")

            if not os.path.exists(model_path):
                logger.warning("Model artifacts not found at %s. Run training first.", model_path)
                cls._is_loaded = False
                return False

            cls._model = joblib.load(model_path)
            cls._scaler = joblib.load(scaler_path)
            cls._encoder = joblib.load(encoder_path)

            if os.path.exists(feature_names_path):
                cls._feature_names = joblib.load(feature_names_path)

            cls._is_loaded = True
            logger.info("ML model loaded successfully [version=%s]", cls._model_version)
            return True

        except Exception as e:
            logger.error("Failed to load ML model: %s", str(e))
            cls._is_loaded = False
            return False

    @classmethod
    def reload_model(cls, app=None):
        """Dynamically reload the model (e.g., after retraining)."""
        logger.info("Reloading ML model...")
        return cls.load_model(app)

    @classmethod
    def is_ready(cls):
        """Check if the model is loaded and ready for predictions."""
        return cls._is_loaded and cls._model is not None

    @classmethod
    def predict(cls, input_data: dict) -> dict:
        """
        Make a sales prediction from validated input data.

        Args:
            input_data: Dictionary with validated input features.

        Returns:
            Dictionary with prediction results.
        """
        if not cls.is_ready():
            raise RuntimeError("Model not loaded. Please train or load the model first.")

        start_time = time.time()

        try:
            # Create DataFrame from input
            df = pd.DataFrame([input_data])

            # Separate numerical and categorical features
            numerical_features = ["item_weight", "item_visibility", "item_mrp", "outlet_establishment_year"]
            categorical_features = ["item_type", "outlet_size", "outlet_location_type", "outlet_type"]

            # Scale numerical features
            numerical_data = df[numerical_features].values
            numerical_scaled = cls._scaler.transform(numerical_data)

            # Encode categorical features
            categorical_data = df[categorical_features]
            categorical_encoded = cls._encoder.transform(categorical_data)

            # Combine features
            if hasattr(categorical_encoded, "toarray"):
                categorical_encoded = categorical_encoded.toarray()

            features = np.hstack([numerical_scaled, categorical_encoded])

            # Make prediction
            prediction = cls._model.predict(features)[0]

            # Ensure non-negative prediction
            prediction = max(0.0, float(prediction))

            # Calculate prediction time
            prediction_time_ms = (time.time() - start_time) * 1000

            # Calculate confidence (based on feature importance if available)
            confidence = cls._calculate_confidence(features)

            result = {
                "predicted_sales": round(prediction, 2),
                "confidence_score": round(confidence, 4),
                "prediction_time_ms": round(prediction_time_ms, 2),
                "model_version": cls._model_version,
                "currency": "INR",
            }

            prediction_logger.info(
                "Prediction: sales=%.2f, confidence=%.4f, time=%.2fms",
                prediction, confidence, prediction_time_ms,
            )

            return result

        except Exception as e:
            logger.error("Prediction failed: %s", str(e))
            raise

    @classmethod
    def batch_predict(cls, inputs: list) -> list:
        """Make batch predictions for multiple inputs."""
        results = []
        for input_data in inputs:
            try:
                result = cls.predict(input_data)
                result["status"] = "success"
            except Exception as e:
                result = {"status": "error", "message": str(e)}
            results.append(result)
        return results

    @classmethod
    def _calculate_confidence(cls, features):
        """Calculate prediction confidence score."""
        try:
            if hasattr(cls._model, "estimators_"):
                # For ensemble models, use prediction variance
                predictions = np.array([
                    tree.predict(features)[0]
                    for tree in cls._model.estimators_
                ])
                std = np.std(predictions)
                mean = np.mean(predictions)
                # Coefficient of variation -> confidence
                cv = std / (abs(mean) + 1e-8)
                confidence = max(0.0, min(1.0, 1.0 - cv))
                return confidence
            return 0.85  # Default confidence
        except Exception:
            return 0.80

    @classmethod
    def get_model_info(cls):
        """Get current model information."""
        return {
            "is_loaded": cls._is_loaded,
            "version": cls._model_version,
            "algorithm": type(cls._model).__name__ if cls._model else None,
            "feature_count": len(cls._feature_names) if cls._feature_names else None,
        }
