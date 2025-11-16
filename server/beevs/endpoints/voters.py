import os
import uuid
from flask import request, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from beevs.response import APIResponse
from beevs import db
from beevs.models import Voter, Election, InstitutionalRecord
from beevs.exceptions import ValidationError, NotFoundError, AuthorizationError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/v1/voters', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_voter():
    """Create a voter. Accepts multipart/form-data with fields:
    - name
    - election_id
    - student_record_id (or registration_number)
    - image (file, required)
    """
    name = (request.form.get('name') or '').strip()
    election_id = request.form.get('election_id')
    student_record_id = request.form.get('student_record_id')

    errors = {}
    if not name:
        errors['name'] = 'Name is required'
    if not election_id:
        errors['election_id'] = 'Election id is required'
    if not student_record_id:
        errors['student_record_id'] = 'Student record id is required'
    if 'image' not in request.files or not request.files['image'] or request.files['image'].filename == '':
        errors['image'] = 'Image is required'

    if errors:
        raise ValidationError(message='Validation failed', errors=errors, status_code=400)

    # validate election and student record
    # validate election
    try:
        election = Election.query.get(int(election_id))
    except Exception:
        election = None
    if not election:
        raise NotFoundError(message='Election not found')

    # student_record_id may be an integer primary key or a registration number string.
    record = None
    reg_input = (student_record_id or '').strip()
    # try integer primary key first
    try:
        rec_id = int(student_record_id)
        record = InstitutionalRecord.query.get(rec_id)
    except Exception:
        record = None

    # fallback: try to find by registration_number
    if not record:
        record = InstitutionalRecord.query.filter_by(registration_number=reg_input).first()

    if not record:
        # If there is no matching institutional record, prevent registration and inform the client
        raise ValidationError(message='Institutional record not found', status_code=400)

    # Require exact match on both name and registration number
    provided_name = name.strip()
    if (record.registration_number.strip() != reg_input) or (record.name.strip() != provided_name):
        raise ValidationError(message='Institutional record not found', status_code=400)

    if record.election_id != int(election_id):
        raise ValidationError(message='Student record does not belong to election', status_code=400)

    # Prevent duplicate registrations: same institutional record in the same election
    existing_voter = Voter.query.filter_by(student_record_id=record.id, election_id=int(election_id)).first()
    if existing_voter:
        raise ValidationError(message='This student is already registered to vote', status_code=400)

    # ensure only students with a record can register
    # (we validated above)

    # no email required; skip uniqueness checks

    # generate wallet if not provided
    wallet_address = request.form.get('wallet_address')
    if not wallet_address:
        wallet_address = None
        for _ in range(5):
            candidate_wallet = uuid.uuid4().hex
            if not Voter.query.filter_by(wallet_address=candidate_wallet).first():
                wallet_address = candidate_wallet
                break
        if not wallet_address:
            raise ValidationError(message='Failed to generate unique wallet address', status_code=500)
    else:
        if Voter.query.filter_by(wallet_address=wallet_address).first():
            raise ValidationError(message='Validation failed', errors={'wallet_address': 'Wallet address already in use'}, status_code=400)

    # handle image
    file = request.files.get('image')
    if not file or not allowed_file(file.filename):
        raise ValidationError(message='Validation failed', errors={'image': 'Invalid image file'}, status_code=400)

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    images_dir = os.path.join(app.root_path, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, new_name)
    file.save(save_path)
    base = request.host_url.rstrip('/')
    image_url = f"{base}/static/images/{new_name}"

    voter = Voter(
        name=name,
        image_url=image_url,
        wallet_address=wallet_address,
        election_id=int(election_id),
        student_record_id=int(record.id)
    )

    db.session.add(voter)
    db.session.commit()

    return APIResponse.success(message='Voter created', data={'voter': voter.to_dict()}, status_code=201)


@app.route('/api/v1/elections/<int:election_id>/voters', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_voters(election_id):
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')
    voters = Voter.query.filter_by(election_id=election_id).order_by(Voter.id.asc()).all()
    return APIResponse.success(data={'voters': [v.to_dict() for v in voters]}, status_code=200)


@app.route('/api/v1/voters/<int:voter_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_voter(voter_id):
    voter = Voter.query.get(voter_id)
    if not voter:
        raise NotFoundError(message='Voter not found')

    # remove image file if present
    if voter.image_url:
        filename = os.path.basename(voter.image_url)
        file_path = os.path.join(app.root_path, 'static', 'images', filename)
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            app.logger.exception('Failed to remove voter image file')

    db.session.delete(voter)
    db.session.commit()
    return APIResponse.success(message='Voter deleted', data=None, status_code=200)
