import os
import uuid
import logging
from datetime import timedelta
from flask import request, current_app as app
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.utils import secure_filename
from beevs.response import APIResponse
from beevs import db
from beevs.models import Voter, Election, InstitutionalRecord
from beevs.exceptions import ValidationError, NotFoundError
from deepface import DeepFace

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/v1/elections/<int:election_id>/vote-auth', methods=['POST'], strict_slashes=False)
def vote_auth(election_id):
    election = Election.query.get(election_id)
    if not election:
        raise ValidationError(message='Election not found')

    reg_no = (request.form.get('registration_number') or '').strip()
    if not reg_no:
        raise ValidationError(message='registration_number is required', status_code=400)

    if 'image' not in request.files or not request.files['image'] or request.files['image'].filename == '':
        raise ValidationError(message='Image is required', status_code=400)

    voter = db.session.query(Voter).join(InstitutionalRecord, Voter.student_record_id == InstitutionalRecord.id).filter(
        InstitutionalRecord.registration_number == reg_no,
        Voter.election_id == election_id
    ).first()
    if not voter:
        raise ValidationError(message='No registered voter found for this registration number', status_code=400)

    if not voter.image_url:
        raise ValidationError(message='No reference image available for this voter. Please register with a photo first.', status_code=400)

    file = request.files.get('image')
    if not file or not allowed_file(file.filename):
        raise ValidationError(message='Validation failed', errors={'image': 'Invalid image file'}, status_code=400)

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    temp_name = f"vote_live_{uuid.uuid4().hex}.{ext}"
    images_dir = os.path.join(app.root_path, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    temp_path = os.path.join(images_dir, temp_name)
    file.save(temp_path)

    try:
        known_filename = os.path.basename(voter.image_url)
        known_path = os.path.join(app.root_path, 'static', 'images', known_filename)

        try:
            result = DeepFace.verify(
                img1_path=known_path,
                img2_path=temp_path,
                model_name='ArcFace',
                detector_backend='retinaface',
                distance_metric='cosine',
                enforce_detection=False
            )
        except ValueError as ve:
            logging.error("Face detection error", exc_info=True)
            # Face wasn't detected in one of the images
            raise ValidationError(message=(
                'Face could not be detected in the image'
            ), status_code=400)
        except Exception as e:
            raise ValidationError(message=f'Face verification failed: {str(e)}', status_code=500)

        is_match = bool(result.get('verified', False))
        distance = result.get('distance')
        threshold = result.get('threshold')

        if not is_match:
            raise ValidationError(message='Face did not match', errors={"error": "Can not authenticate! Face did not match"}, status_code=401)

        token = create_access_token(identity=f"voter:{voter.id}", additional_claims={'vote_auth': True, 'election_id': election_id, 'voter_id': voter.id}, expires_delta=timedelta(minutes=10))

        return APIResponse.success(message='Voter authenticated', data={'token': token}, status_code=200)
    finally:
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            app.logger.exception('Failed to remove temporary live image')


@app.route('/api/v1/voters', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_voter():
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

    try:
        election = Election.query.get(int(election_id))
    except Exception:
        election = None
    if not election:
        raise NotFoundError(message='Election not found')

    record = None
    reg_input = (student_record_id or '').strip()
    try:
        rec_id = int(student_record_id)
        record = InstitutionalRecord.query.get(rec_id)
    except Exception:
        record = None

    if not record:
        record = InstitutionalRecord.query.filter_by(registration_number=reg_input, election_id=int(election_id)).first()

    if not record:
        raise ValidationError(message='Institutional record not found', status_code=400)

    provided_name = name.strip()
    if (record.registration_number.strip() != reg_input) or (record.name.strip() != provided_name):
        raise ValidationError(message='Institutional record not found', status_code=400)

    if record.election_id != int(election_id):
        raise ValidationError(message='Student record does not belong to election', status_code=400)

    existing_voter = Voter.query.filter_by(student_record_id=record.id, election_id=int(election_id)).first()
    if existing_voter:
        raise ValidationError(message='This student is already registered to vote', status_code=400)

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
