"""
API Routes
All REST API endpoints for the Sales Prediction System.
"""

import os
import uuid
import time
import logging
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from marshmallow import ValidationError

from app.models.schemas import PredictionInputSchema, BatchPredictionSchema
from app.services.prediction_service import PredictionService
from app.services.training_service import TrainingService
from app.models import db, PredictionRecord, APILog

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)
prediction_schema = PredictionInputSchema()
batch_schema = BatchPredictionSchema()


# ─────────────────────────────────────────────
#  Frontend Serving
# ─────────────────────────────────────────────

@api_bp.route("/")
def serve_frontend():
    """Serve the frontend UI.
    ---
    tags:
      - Frontend
    responses:
      200:
        description: Returns the frontend HTML page
    """
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend"
    )
    return send_from_directory(frontend_dir, "index.html")


@api_bp.route("/css/<path:filename>")
def serve_css(filename):
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "css"
    )
    return send_from_directory(frontend_dir, filename)


@api_bp.route("/js/<path:filename>")
def serve_js(filename):
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "js"
    )
    return send_from_directory(frontend_dir, filename)


@api_bp.route("/assets/<path:filename>")
def serve_assets(filename):
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "assets"
    )
    return send_from_directory(frontend_dir, filename)


# ─────────────────────────────────────────────
#  Health Check
# ─────────────────────────────────────────────

@api_bp.route("/health", methods=["GET"])
@api_bp.route("/api/health", methods=["GET"])
def health_check():
    """API Health Check endpoint.
    ---
    tags:
      - System
    responses:
      200:
        description: API is healthy
        schema:
          properties:
            success:
              type: boolean
            status:
              type: string
            model:
              type: object
    """
    model_info = PredictionService.get_model_info()
    training_status = TrainingService.get_status()

    return jsonify({
        "success": True,
        "status": "healthy",
        "model": model_info,
        "training": training_status,
        "version": "1.0.0",
    }), 200


# ─────────────────────────────────────────────
#  Prediction Endpoint
# ─────────────────────────────────────────────

@api_bp.route("/predict", methods=["POST"])
@api_bp.route("/api/predict", methods=["POST"])
def predict():
    """Make a sales prediction.
    ---
    tags:
      - Predictions
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - item_weight
            - item_visibility
            - item_mrp
            - item_type
            - outlet_size
            - outlet_location_type
            - outlet_type
            - outlet_establishment_year
          properties:
            item_weight:
              type: number
              example: 12.5
              description: Weight of the item (0.1 - 50.0 kg)
            item_visibility:
              type: number
              example: 0.05
              description: Display area percentage (0.0 - 0.35)
            item_mrp:
              type: number
              example: 150.0
              description: Maximum Retail Price (10.0 - 300.0)
            item_type:
              type: string
              example: "Dairy"
              description: Category of the item
            outlet_size:
              type: string
              example: "Medium"
              description: Size of outlet
            outlet_location_type:
              type: string
              example: "Tier 1"
              description: Location tier
            outlet_type:
              type: string
              example: "Supermarket Type1"
              description: Type of outlet
            outlet_establishment_year:
              type: integer
              example: 2005
              description: Year outlet was established
    responses:
      200:
        description: Prediction result
      422:
        description: Validation error
      503:
        description: Model not loaded
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())[:12]

    try:
        # Parse and validate input
        json_data = request.get_json(force=True)
        if not json_data:
            return jsonify({
                "success": False,
                "error": {"code": 400, "message": "Request body is required."},
            }), 400

        validated_data = prediction_schema.load(json_data)

        # Check model readiness
        if not PredictionService.is_ready():
            return jsonify({
                "success": False,
                "error": {"code": 503, "message": "Model not loaded. Please train the model first."},
            }), 503

        # Make prediction
        result = PredictionService.predict(validated_data)

        # Store prediction record
        try:
            record = PredictionRecord(
                request_id=request_id,
                item_weight=validated_data["item_weight"],
                item_visibility=validated_data["item_visibility"],
                item_mrp=validated_data["item_mrp"],
                item_type=validated_data["item_type"],
                outlet_size=validated_data["outlet_size"],
                outlet_location_type=validated_data["outlet_location_type"],
                outlet_type=validated_data["outlet_type"],
                outlet_establishment_year=validated_data["outlet_establishment_year"],
                predicted_sales=result["predicted_sales"],
                confidence_score=result["confidence_score"],
                prediction_time_ms=result["prediction_time_ms"],
                model_version=result["model_version"],
                ip_address=request.remote_addr,
            )
            db.session.add(record)
            db.session.commit()
        except Exception as db_err:
            logger.warning("Failed to store prediction record: %s", str(db_err))
            db.session.rollback()

        # Log API call
        _log_api_call("/predict", "POST", 200, (time.time() - start_time) * 1000)

        return jsonify({
            "success": True,
            "request_id": request_id,
            "data": result,
        }), 200

    except ValidationError as e:
        _log_api_call("/predict", "POST", 422, (time.time() - start_time) * 1000, str(e.messages))
        return jsonify({
            "success": False,
            "error": {
                "code": 422,
                "type": "Validation Error",
                "message": "Input validation failed.",
                "details": e.messages,
            },
        }), 422

    except Exception as e:
        logger.error("Prediction endpoint error: %s", str(e))
        _log_api_call("/predict", "POST", 500, (time.time() - start_time) * 1000, str(e))
        return jsonify({
            "success": False,
            "error": {"code": 500, "message": "Prediction failed. Please try again."},
        }), 500


# ─────────────────────────────────────────────
#  Batch Prediction
# ─────────────────────────────────────────────

@api_bp.route("/api/predict/batch", methods=["POST"])
def batch_predict():
    """Make batch sales predictions.
    ---
    tags:
      - Predictions
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            predictions:
              type: array
              items:
                type: object
    responses:
      200:
        description: Batch prediction results
    """
    try:
        json_data = request.get_json(force=True)
        validated_data = batch_schema.load(json_data)

        if not PredictionService.is_ready():
            return jsonify({
                "success": False,
                "error": {"code": 503, "message": "Model not loaded."},
            }), 503

        results = PredictionService.batch_predict(validated_data["predictions"])

        return jsonify({
            "success": True,
            "count": len(results),
            "data": results,
        }), 200

    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": {"code": 422, "details": e.messages},
        }), 422

    except Exception as e:
        logger.error("Batch prediction error: %s", str(e))
        return jsonify({
            "success": False,
            "error": {"code": 500, "message": str(e)},
        }), 500


# ─────────────────────────────────────────────
#  Training Endpoint
# ─────────────────────────────────────────────

@api_bp.route("/train", methods=["POST"])
@api_bp.route("/api/train", methods=["POST"])
def train_model():
    """Retrain the ML model.
    ---
    tags:
      - Training
    responses:
      200:
        description: Training completed successfully
      409:
        description: Training already in progress
      500:
        description: Training failed
    """
    if TrainingService.is_training():
        return jsonify({
            "success": False,
            "error": {"code": 409, "message": "Training already in progress."},
        }), 409

    result = TrainingService.train_model(app=current_app._get_current_object())

    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


# ─────────────────────────────────────────────
#  Prediction History
# ─────────────────────────────────────────────

@api_bp.route("/api/predictions/history", methods=["GET"])
def prediction_history():
    """Get prediction history.
    ---
    tags:
      - Predictions
    parameters:
      - name: limit
        in: query
        type: integer
        default: 20
      - name: offset
        in: query
        type: integer
        default: 0
    responses:
      200:
        description: List of past predictions
    """
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    records = (
        PredictionRecord.query
        .order_by(PredictionRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = PredictionRecord.query.count()

    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in records],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }), 200


# ─────────────────────────────────────────────
#  Analytics
# ─────────────────────────────────────────────

@api_bp.route("/api/analytics/summary", methods=["GET"])
def analytics_summary():
    """Get analytics summary.
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Analytics summary data
    """
    try:
        total_predictions = PredictionRecord.query.count()

        if total_predictions == 0:
            return jsonify({
                "success": True,
                "data": {
                    "total_predictions": 0,
                    "avg_sales": 0,
                    "max_sales": 0,
                    "min_sales": 0,
                    "avg_confidence": 0,
                    "avg_response_time_ms": 0,
                },
            }), 200

        from sqlalchemy import func

        stats = db.session.query(
            func.avg(PredictionRecord.predicted_sales).label("avg_sales"),
            func.max(PredictionRecord.predicted_sales).label("max_sales"),
            func.min(PredictionRecord.predicted_sales).label("min_sales"),
            func.avg(PredictionRecord.confidence_score).label("avg_confidence"),
            func.avg(PredictionRecord.prediction_time_ms).label("avg_response_time"),
        ).first()

        return jsonify({
            "success": True,
            "data": {
                "total_predictions": total_predictions,
                "avg_sales": round(float(stats.avg_sales or 0), 2),
                "max_sales": round(float(stats.max_sales or 0), 2),
                "min_sales": round(float(stats.min_sales or 0), 2),
                "avg_confidence": round(float(stats.avg_confidence or 0), 4),
                "avg_response_time_ms": round(float(stats.avg_response_time or 0), 2),
            },
        }), 200

    except Exception as e:
        logger.error("Analytics error: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _log_api_call(endpoint, method, status_code, response_time_ms, error_message=None):
    """Log API call to database."""
    try:
        log = APILog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=request.remote_addr if request else None,
            error_message=error_message,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.warning("Failed to log API call: %s", str(e))
        db.session.rollback()
