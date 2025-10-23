"""
Custom exceptions for the BEEVS application
"""


class ValidationError(Exception):
    """
    Custom validation error exception
    Used for request validation failures
    """
    def __init__(self, message="Validation failed", errors=None, status_code=400):
        self.message = message
        self.errors = errors or {}
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(Exception):
    """
    Custom authentication error exception
    Used for authentication failures
    """
    def __init__(self, message="Authentication failed", status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthorizationError(Exception):
    """
    Custom authorization error exception
    Used for permission/access control failures
    """
    def __init__(self, message="Access denied", status_code=403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    Custom not found error exception
    Used when resources are not found
    """
    def __init__(self, message="Resource not found", status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
