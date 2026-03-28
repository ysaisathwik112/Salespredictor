"""
Global Error Handlers
Provides structured JSON error responses for all exception types.
"""

import logging
import traceback
from flask import jsonify
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        logger.warning("Bad request: %s", str(error))
        return jsonify({
            "success": False,
            "error": {
                "code": 400,
                "type": "Bad Request",
                "message": str(error.description) if hasattr(error, "description") else str(error),
            }
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": {
                "code": 404,
                "type": "Not Found",
                "message": "The requested resource was not found.",
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": {
                "code": 405,
                "type": "Method Not Allowed",
                "message": "The HTTP method is not allowed for this endpoint.",
            }
        }), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        logger.warning("Rate limit exceeded: %s", str(error))
        return jsonify({
            "success": False,
            "error": {
                "code": 429,
                "type": "Rate Limit Exceeded",
                "message": "Too many requests. Please try again later.",
            }
        }), 429

    @app.errorhandler(ValidationError)
    def validation_error(error):
        logger.warning("Validation error: %s", error.messages)
        return jsonify({
            "success": False,
            "error": {
                "code": 422,
                "type": "Validation Error",
                "message": "Input validation failed.",
                "details": error.messages,
            }
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error: %s\n%s", str(error), traceback.format_exc())
        return jsonify({
            "success": False,
            "error": {
                "code": 500,
                "type": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        }), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        logger.error("Unhandled exception: %s\n%s", str(error), traceback.format_exc())
        return jsonify({
            "success": False,
            "error": {
                "code": 500,
                "type": "Internal Server Error",
                "message": "An unexpected error occurred.",
            }
        }), 500
