from flask import current_app as app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from beevs.response import APIResponse
from beevs import db
from beevs.models import Election
from beevs.exceptions import ValidationError, AuthorizationError
from datetime import datetime


@app.route('/api/v1/elections', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_election():
    data = request.get_json()
    if not data:
        raise ValidationError(message="Invalid request format", errors={"format": "JSON payload required"}, status_code=400)

    title = (data.get('title') or '').strip()
    scheduled_for = data.get('scheduled_for')
    starts_at_raw = data.get('starts_at') or data.get('start_time')
    ends_at_raw = data.get('ends_at') or data.get('end_time')

    errors = {}
    if not title:
        errors['title'] = 'Title is required'
    if not scheduled_for:
        errors['scheduled_for'] = 'Scheduled date is required'

    if errors:
        raise ValidationError(message='Validation failed', errors=errors, status_code=400)

    # parse scheduled_for date
    try:
        scheduled_for_date = datetime.strptime(scheduled_for, '%Y-%m-%d').date()
    except Exception:
        raise ValidationError(message='Validation failed', errors={'scheduled_for': 'Invalid date format, expected YYYY-MM-DD'}, status_code=400)

    # parse starts_at / ends_at if provided
    starts_at = None
    ends_at = None
    try:
        if starts_at_raw:
            # Accept ISO format
            starts_at = datetime.fromisoformat(starts_at_raw)
    except Exception:
        # Try combining scheduled_for + time
        try:
            starts_at = datetime.strptime(f"{scheduled_for} {starts_at_raw}", '%Y-%m-%d %H:%M')
        except Exception:
            raise ValidationError(message='Validation failed', errors={'starts_at': 'Invalid datetime format'}, status_code=400)

    try:
        if ends_at_raw:
            ends_at = datetime.fromisoformat(ends_at_raw)
    except Exception:
        try:
            ends_at = datetime.strptime(f"{scheduled_for} {ends_at_raw}", '%Y-%m-%d %H:%M')
        except Exception:
            raise ValidationError(message='Validation failed', errors={'ends_at': 'Invalid datetime format'}, status_code=400)

    # Authorization: only super_admins can create elections
    claims = get_jwt()
    role = claims.get('role')
    if role != 'super_admin':
        raise AuthorizationError(message='Only super admins can create elections')

    # The identity was stored as a string when the token was created; cast
    # it back to int for DB relationships.
    admin_id_raw = get_jwt_identity()
    try:
        admin_id = int(admin_id_raw)
    except Exception:
        raise AuthorizationError(message='Invalid token identity')

    election = Election(
        title=title,
        scheduled_for=scheduled_for_date,
        starts_at=starts_at,
        ends_at=ends_at,
        super_admin_id=admin_id
    )

    db.session.add(election)
    db.session.commit()

    return APIResponse.success(message='Election created', data=election.to_dict(), status_code=201)


@app.route('/api/v1/elections', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_elections():
    """
    List elections. Returns all elections for now.
    """
    # identity stored as string in token
    admin_id_raw = get_jwt_identity()
    try:
        admin_id = int(admin_id_raw)
    except Exception:
        raise AuthorizationError(message='Invalid token identity')

    # For now, return all elections. Later we can filter by admin or add pagination.
    elections = Election.query.order_by(Election.created_at.desc()).all()
    data = [e.to_dict() for e in elections]

    return APIResponse.success(message='Elections fetched', data={'elections': data}, status_code=200)
