"""
Training Service
Handles model retraining from the API layer.
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TrainingService:
    """Service for managing model training and retraining."""

    _is_training = False
    _last_training = None

    @classmethod
    def is_training(cls):
        return cls._is_training

    @classmethod
    def train_model(cls, app=None):
        """
        Trigger model retraining.
        Returns training metrics on success.
        """
        if cls._is_training:
            return {
                "success": False,
                "message": "Training already in progress. Please wait.",
            }

        cls._is_training = True
        logger.info("Starting model retraining...")

        try:
            # Run training script
            train_script = os.path.join(PROJECT_ROOT, "ml", "training", "train.py")

            result = subprocess.run(
                [sys.executable, train_script],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=PROJECT_ROOT,
            )

            if result.returncode != 0:
                logger.error("Training failed: %s", result.stderr)
                return {
                    "success": False,
                    "message": f"Training failed: {result.stderr[:500]}",
                }

            # Parse metrics from stdout
            metrics = cls._parse_training_output(result.stdout)

            # Reload model
            if app:
                from app.services.prediction_service import PredictionService
                PredictionService.reload_model(app)

            cls._last_training = datetime.now(timezone.utc).isoformat()

            logger.info("Model retraining completed successfully")
            return {
                "success": True,
                "message": "Model retrained successfully.",
                "metrics": metrics,
                "trained_at": cls._last_training,
            }

        except subprocess.TimeoutExpired:
            logger.error("Training timed out after 300 seconds")
            return {
                "success": False,
                "message": "Training timed out. Please try with smaller dataset.",
            }
        except Exception as e:
            logger.error("Training error: %s", str(e))
            return {
                "success": False,
                "message": f"Training error: {str(e)}",
            }
        finally:
            cls._is_training = False

    @classmethod
    def _parse_training_output(cls, output):
        """Parse metrics from training script output."""
        metrics = {}
        for line in output.strip().split("\n"):
            if "R2 Score" in line:
                try:
                    metrics["r2_score"] = float(line.split(":")[-1].strip())
                except (ValueError, IndexError):
                    pass
            elif "RMSE" in line:
                try:
                    metrics["rmse"] = float(line.split(":")[-1].strip())
                except (ValueError, IndexError):
                    pass
            elif "MAE" in line:
                try:
                    metrics["mae"] = float(line.split(":")[-1].strip())
                except (ValueError, IndexError):
                    pass
        return metrics

    @classmethod
    def get_status(cls):
        """Get training status."""
        return {
            "is_training": cls._is_training,
            "last_training": cls._last_training,
        }
