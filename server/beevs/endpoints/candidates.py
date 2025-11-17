import os
import uuid
from flask import current_app as app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from beevs.response import APIResponse
from beevs import db
from beevs.models import Candidate, Election, Post, Vote
from beevs.contract import ContractService
from hexbytes import HexBytes
from beevs.exceptions import ValidationError, AuthorizationError, NotFoundError


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/v1/candidates', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_candidate():
    """
    Create a candidate. Accepts multipart/form-data with fields:
    - name
    - wallet_address (optional; will be generated if not provided)
    - election_id
    - post_id
    - image (file, required)
    """
    # Use form data so we can accept file uploads
    name = (request.form.get('name') or '').strip()
    wallet_address = (request.form.get('wallet_address') or '').strip()
    election_id = request.form.get('election_id')
    post_id = request.form.get('post_id')

    errors = {}
    if not name:
        errors['name'] = 'Name is required'
    if not election_id:
        errors['election_id'] = 'Election id is required'
    if not post_id:
        errors['post_id'] = 'Post id is required'

    # image is required
    if 'image' not in request.files or not request.files['image'] or request.files['image'].filename == '':
        errors['image'] = 'Image is required'

    if errors:
        raise ValidationError(message='Validation failed', errors=errors, status_code=400)

    # Validate election and post
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError(message='Post not found')
    if post.election_id != int(election_id):
        raise ValidationError(message='Validation failed', errors={'post_id': 'Post does not belong to election'}, status_code=400)

    # Authorization: any logged-in admin may create a candidate (per earlier decision)
    admin_id_raw = get_jwt_identity()
    try:
        admin_id = int(admin_id_raw)
    except Exception:
        raise AuthorizationError(message='Invalid token identity')

    # If wallet_address not provided, generate one server-side and ensure uniqueness
    if not wallet_address:
        wallet_address = None
        for _ in range(5):
            candidate_wallet = uuid.uuid4().hex
            if not Candidate.query.filter_by(wallet_address=candidate_wallet).first():
                wallet_address = candidate_wallet
                break
        if not wallet_address:
            raise ValidationError(message='Failed to generate unique wallet address', status_code=500)
    else:
        # Check wallet uniqueness if provided
        existing = Candidate.query.filter_by(wallet_address=wallet_address).first()
        if existing:
            raise ValidationError(message='Validation failed', errors={'wallet_address': 'Wallet address already in use'}, status_code=400)

    # image handling (required)
    image_url = None
    file = request.files.get('image')
    if not file:
        # Shouldn't happen because we validated earlier, but double-check
        raise ValidationError(message='Validation failed', errors={'image': 'Image is required'}, status_code=400)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_name = f"{uuid.uuid4().hex}.{ext}"
        images_dir = os.path.join(app.root_path, 'static', 'images')
        os.makedirs(images_dir, exist_ok=True)
        save_path = os.path.join(images_dir, new_name)
        file.save(save_path)
        # Return a full URL pointing to the API host so the frontend can load images
        base = request.host_url.rstrip('/')
        image_url = f"{base}/static/images/{new_name}"
    else:
        raise ValidationError(message='Validation failed', errors={'image': 'Invalid image file'}, status_code=400)

    candidate = Candidate(
        name=name,
        wallet_address=wallet_address,
        image_url=image_url,
        election_id=int(election_id),
        post_id=int(post_id)
    )

    db.session.add(candidate)
    db.session.commit()

    # Attempt to add candidate on-chain if the election has an onchain_id and contract is configured
    try:
        if election.onchain_id:
            cs = ContractService()
            # send transaction: addCandidate(uint256 electionId, string name)
            res = cs.send_transaction('addCandidate', [int(election.onchain_id), candidate.name], wait_for_receipt=True, timeout=120)
            tx_hash = res.get('tx_hash')
            receipt = res.get('receipt')

            # record a Vote-like tx record for auditing
            vote = Vote(
                election_id=election.id,
                voter_id=None,
                candidate_id=candidate.id,
                action='add_candidate',
                tx_hash=tx_hash,
                status='pending'
            )

            if receipt:
                # sanitize receipt: convert HexBytes/bytes to hex strings
                def _sanitize(obj):
                    if obj is None:
                        return None
                    if isinstance(obj, HexBytes) or isinstance(obj, (bytes, bytearray)):
                        return '0x' + bytes(obj).hex()
                    if isinstance(obj, dict):
                        return {k: _sanitize(v) for k, v in dict(obj).items()}
                    if isinstance(obj, (list, tuple, set)):
                        return [_sanitize(v) for v in obj]
                    if isinstance(obj, (str, int, float, bool)):
                        return obj
                    try:
                        return str(obj)
                    except Exception:
                        return None

                vote.receipt = _sanitize(receipt)

                # try parse event
                try:
                    contract = cs.get_contract()
                    events = contract.events.CandidateAdded().process_receipt(receipt)
                    if events:
                        evt = events[0]
                        onchain_cid = int(evt['args'].get('candidateId') or evt['args'].get('candidateId'))
                        candidate.onchain_id = onchain_cid
                        vote.status = 'confirmed'
                        vote.block_number = int(receipt.get('blockNumber')) if receipt.get('blockNumber') else None
                except Exception:
                    # leave candidate.onchain_id unset; keep vote pending with receipt
                    app.logger.exception('Failed to parse candidate add event')

            db.session.add(vote)
            db.session.add(candidate)
            db.session.commit()

    except Exception:
        # Propagate contract errors so caller can see them — do not silently swallow
        app.logger.exception('Failed to create candidate on-chain')
        raise

    return APIResponse.success(message='Candidate created', data={'candidate': candidate.to_dict()}, status_code=201)


@app.route('/api/v1/candidates/<int:candidate_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_candidate(candidate_id):
    """
    Delete a candidate. Any logged-in admin may delete.
    Also attempts to remove the candidate image file if present.
    """
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        raise NotFoundError(message='Candidate not found')

    # attempt to remove the image file by filename (works whether image_url is absolute or relative)
    if candidate.image_url:
        filename = os.path.basename(candidate.image_url)
        file_path = os.path.join(app.root_path, 'static', 'images', filename)
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            app.logger.exception('Failed to remove candidate image file')

    db.session.delete(candidate)
    db.session.commit()

    return APIResponse.success(message='Candidate deleted', data=None, status_code=200)
