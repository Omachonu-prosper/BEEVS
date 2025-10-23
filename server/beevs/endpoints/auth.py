from flask import current_app as app, request
from flask_jwt_extended import create_access_token, create_refresh_token
from beevs.response import APIResponse
from beevs.models import Admin
from beevs.utils import validate_login
from beevs.exceptions import AuthenticationError


@app.route('/api/v1/auth/login', methods=['POST'], strict_slashes=False)
def login():
    """
    Admin login endpoint
    Expected JSON payload:
    {
        "email": "admin@example.com",
        "password": "password123"
    }
    """
    data = request.get_json()
    email, password = validate_login(data)
    admin = Admin.query.filter_by(email=email).first()
    
    if not admin:
        raise AuthenticationError(
            message="Invalid credentials",
            status_code=401
        )
    
    if not admin.check_password(password):
        raise AuthenticationError(
            message="Invalid credentials",
            status_code=401
        )
    
    additional_claims = {
        "role": admin.role.value,
        "email": admin.email
    }
    access_token = create_access_token(
        identity=admin.id,
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(identity=admin.id)
    
    # Prepare response data
    admin_data = {
        'id': admin.id,
        'name': admin.name,
        'email': admin.email,
        'role': admin.role.value,
        'is_super_admin': admin.is_super_admin(),
        'created_at': admin.created_at.isoformat() if admin.created_at else None
    }
    
    return APIResponse.success(
        message="Login successful",
        data={
            'admin': admin_data,
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer'
            }
        },
        status_code=200
    )