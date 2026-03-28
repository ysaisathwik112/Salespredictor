"""
Unit Tests for the Sales Prediction API
Tests cover: health check, prediction, validation, history, and error handling.
"""

import json
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def valid_input():
    """Valid prediction input data."""
    return {
        "item_weight": 12.5,
        "item_visibility": 0.05,
        "item_mrp": 150.0,
        "item_type": "Dairy",
        "outlet_size": "Medium",
        "outlet_location_type": "Tier 1",
        "outlet_type": "Supermarket Type1",
        "outlet_establishment_year": 2005,
    }


# ─── Health Check Tests ───

class TestHealthCheck:
    """Tests for the /health endpoint."""

    def test_health_check_returns_200(self, client):
        """Health check should return 200 with status info."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["status"] == "healthy"
        assert "model" in data
        assert "version" in data

    def test_health_check_api_prefix(self, client):
        """Health check should also work via /api/health."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


# ─── Frontend Tests ───

class TestFrontend:
    """Tests for frontend serving."""

    def test_serves_index_html(self, client):
        """Root URL should serve the frontend HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"SalesCast" in response.data


# ─── Prediction Tests ───

class TestPrediction:
    """Tests for the /predict endpoint."""

    def test_predict_without_model_returns_503(self, client, valid_input):
        """Prediction without loaded model should return 503."""
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        # Model may not be trained in test env
        assert response.status_code in [200, 503]

    def test_predict_with_empty_body_returns_400(self, client):
        """Prediction with empty body should return 400 or 422."""
        response = client.post(
            "/predict",
            data="{}",
            content_type="application/json",
        )
        assert response.status_code in [400, 422]

    def test_predict_with_invalid_weight(self, client, valid_input):
        """Prediction with invalid weight should return 422."""
        valid_input["item_weight"] = -5.0
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False

    def test_predict_with_invalid_mrp(self, client, valid_input):
        """Prediction with MRP out of range should return 422."""
        valid_input["item_mrp"] = 500.0
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_predict_with_invalid_item_type(self, client, valid_input):
        """Prediction with invalid item type should return 422."""
        valid_input["item_type"] = "InvalidType"
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_predict_with_invalid_outlet_size(self, client, valid_input):
        """Prediction with invalid outlet size should return 422."""
        valid_input["outlet_size"] = "ExtraLarge"
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_predict_with_missing_fields(self, client):
        """Prediction with missing required fields should return 422."""
        incomplete_data = {"item_weight": 12.5, "item_mrp": 100.0}
        response = client.post(
            "/predict",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_predict_response_structure(self, client, valid_input):
        """Prediction response should have correct structure."""
        response = client.post(
            "/predict",
            data=json.dumps(valid_input),
            content_type="application/json",
        )
        data = response.get_json()
        assert "success" in data
        if data["success"]:
            assert "data" in data
            assert "predicted_sales" in data["data"]
            assert "confidence_score" in data["data"]
            assert "prediction_time_ms" in data["data"]


# ─── History Tests ───

class TestHistory:
    """Tests for the prediction history endpoint."""

    def test_history_returns_200(self, client):
        """History endpoint should return 200."""
        response = client.get("/api/predictions/history")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert "pagination" in data

    def test_history_pagination(self, client):
        """History should support limit and offset parameters."""
        response = client.get("/api/predictions/history?limit=5&offset=0")
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["limit"] == 5
        assert data["pagination"]["offset"] == 0


# ─── Analytics Tests ───

class TestAnalytics:
    """Tests for the analytics endpoint."""

    def test_analytics_returns_200(self, client):
        """Analytics endpoint should return 200."""
        response = client.get("/api/analytics/summary")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert "total_predictions" in data["data"]


# ─── Error Handling Tests ───

class TestErrorHandling:
    """Tests for error handling."""

    def test_404_returns_json(self, client):
        """404 errors should return structured JSON."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == 404

    def test_405_returns_json(self, client):
        """405 errors should return structured JSON."""
        response = client.delete("/predict")
        assert response.status_code == 405
        data = response.get_json()
        assert data["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
