from flask import current_app as app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from beevs.response import APIResponse
from beevs import db
from beevs.models import Post, Election, Candidate
from beevs.exceptions import ValidationError, AuthorizationError, NotFoundError
from datetime import datetime


@app.route('/api/v1/posts', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_post():
    """
    Create a post/position for an election
    Body: { title, election_id }
    Only the super_admin of the election may create posts.
    """
    data = request.get_json()
    if not data:
        raise ValidationError(message="Invalid request format", errors={"format": "JSON payload required"}, status_code=400)

    title = (data.get('title') or '').strip()
    election_id = data.get('election_id')

    errors = {}
    if not title:
        errors['title'] = 'Title is required'
    if not election_id:
        errors['election_id'] = 'Election id is required'

    if errors:
        raise ValidationError(message='Validation failed', errors=errors, status_code=400)

    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    # Only the super_admin assigned to the election can create posts
    admin_id_raw = get_jwt_identity()
    try:
        admin_id = int(admin_id_raw)
    except Exception:
        raise AuthorizationError(message='Invalid token identity')

    if election.super_admin_id != admin_id:
        raise AuthorizationError(message='Only the election super admin can create posts')

    post = Post(title=title, election_id=election_id)
    db.session.add(post)
    db.session.commit()

    return APIResponse.success(message='Post created', data={'post': post.to_dict()}, status_code=201)


@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_post(post_id):
    """
    Delete a post and cascade-delete its candidates (DB cascade)
    Any logged-in admin can delete (per requirements).
    """
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError(message='Post not found')

    # Authorization: any logged-in admin may delete
    # confirm existence of election
    election = Election.query.get(post.election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    # Delete the post (candidates will be cascaded by DB)
    db.session.delete(post)
    db.session.commit()

    return APIResponse.success(message='Post deleted', data=None, status_code=200)


@app.route('/api/v1/elections/<int:election_id>/posts', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_posts(election_id):
    """
    List posts for an election. Query param include_candidates=true will include nested candidates
    """
    include_candidates = request.args.get('include_candidates', 'false').lower() == 'true'

    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    posts = Post.query.filter_by(election_id=election_id).order_by(Post.created_at.asc()).all()
    data = []
    for p in posts:
        if include_candidates:
            candidates = [c.to_dict() for c in p.candidates]
            item = p.to_dict()
            item['candidates'] = candidates
        else:
            item = p.to_dict()
            item['candidate_count'] = len(p.candidates)
        data.append(item)

    return APIResponse.success(message='Posts fetched', data={'posts': data}, status_code=200)
