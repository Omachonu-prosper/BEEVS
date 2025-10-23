import re
from beevs.exceptions import ValidationError


def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_login(data):
    """
    Validate login data and raise ValidationError if invalid
    
    Args:
        data (dict): Request data containing email and password
        
    Raises:
        ValidationError: If validation fails
        
    Returns:
        tuple: (email, password) if validation passes
    """
    if not data:
        raise ValidationError(
            message="Invalid request format",
            errors={"format": "JSON payload required"},
            status_code=400
        )
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate required fields
    errors = {}
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Invalid email format'
        
    if not password:
        errors['password'] = 'Password is required'
        
    if errors:
        raise ValidationError(
            message="Validation failed",
            errors=errors,
            status_code=400
        )
    
    return email, password


def validate_password_strength(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"
