"""
Error handlers for the BEEVS application
"""

from flask import current_app as app
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from beevs.response import APIResponse
from beevs.exceptions import ValidationError, AuthenticationError, AuthorizationError, NotFoundError
from beevs import jwt


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle ValidationError exceptions"""
    return APIResponse.error(
        message=error.message,
        errors=error.errors,
        status_code=error.status_code
    )


@app.errorhandler(AuthenticationError)
def handle_authentication_error(error):
    """Handle AuthenticationError exceptions"""
    return APIResponse.error(
        message=error.message,
        errors={"authentication": error.message},
        status_code=error.status_code
    )


@app.errorhandler(AuthorizationError)
def handle_authorization_error(error):
    """Handle AuthorizationError exceptions"""
    return APIResponse.error(
        message=error.message,
        errors={"authorization": error.message},
        status_code=error.status_code
    )


@app.errorhandler(NotFoundError)
def handle_not_found_error(error):
    """Handle NotFoundError exceptions"""
    return APIResponse.error(
        message=error.message,
        errors={"resource": error.message},
        status_code=error.status_code
    )


@app.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors"""
    return APIResponse.error(
        message="Internal server error",
        errors={"server": "An unexpected error occurred"},
        status_code=500
    )


@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors"""
    return APIResponse.error(
        message="Endpoint not found",
        errors={"endpoint": "The requested endpoint does not exist"},
        status_code=404
    )


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """Handle method not allowed errors"""
    return APIResponse.error(
        message="Method not allowed",
        errors={"method": "The HTTP method is not allowed for this endpoint"},
        status_code=405
    )


@app.errorhandler(JWTExtendedException)
def handle_jwt_exceptions(error):
    """Handle JWT related exceptions"""
    return APIResponse.error(
        message="Authentication error",
        errors={"jwt": str(error)},
        status_code=401
    )


# JWT callbacks for custom error handling
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT tokens"""
    return APIResponse.error(
        message="Token has expired",
        errors={"jwt": "Please login again"},
        status_code=401
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT tokens"""
    return APIResponse.error(
        message="Invalid token",
        errors={"jwt": str(error)},
        status_code=401
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing JWT tokens"""
    return APIResponse.error(
        message="Authorization token required",
        errors={"jwt": "Please provide a valid token"},
        status_code=401
    )
