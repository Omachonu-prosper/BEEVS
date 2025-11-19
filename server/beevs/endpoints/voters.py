import os
import uuid
import logging
from datetime import timedelta
from flask import request, current_app as app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt
from werkzeug.utils import secure_filename
from beevs.response import APIResponse
from beevs import db
from beevs.models import Voter, Election, InstitutionalRecord, Post, Candidate, Vote
from beevs.exceptions import ValidationError, NotFoundError
from deepface import DeepFace
from beevs.contract import ContractService
from hexbytes import HexBytes
from web3.exceptions import ContractLogicError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _extract_revert_reason(exc: Exception) -> str:
    """Try to extract a human-friendly revert reason from a ContractLogicError.

    Handles common web3 exception patterns:
    - message containing 'execution reverted: <reason>'
    - data payload containing ABI-encoded Error(string) (0x08c379a0...)
    Falls back to str(exc) if parsing fails.
    """
    try:
        # First try the standard message pattern
        msg = str(exc.args[0]) if exc.args else str(exc)
        if 'execution reverted' in msg:
            parts = msg.split('execution reverted: ')
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip()

        # Next, check for ABI-encoded revert data in second arg
        if len(exc.args) > 1:
            data = exc.args[1]
            hexdata = None
            if isinstance(data, (bytes, bytearray)):
                hexdata = data.hex()
            else:
                hexdata = str(data)
            if hexdata and hexdata.startswith('0x08c379a0'):
                # remove 0x and method id (8 chars) -> payload
                clean = hexdata[10:] if hexdata.startswith('0x') else hexdata[8:]
                # skip offset (32 bytes = 64 chars), then read length (next 32 bytes)
                try:
                    str_len_hex = clean[64:128]
                    str_len = int(str_len_hex, 16)
                    str_hex = clean[128:128 + str_len * 2]
                    reason = bytes.fromhex(str_hex).decode('utf-8', errors='replace')
                    return reason
                except Exception:
                    pass
    except Exception:
        pass
    return str(exc)


@app.route('/api/v1/elections/<int:election_id>/vote-auth', methods=['POST'], strict_slashes=False)
def vote_auth(election_id):
    election = Election.query.get(election_id)
    if not election:
        raise ValidationError(message='Election not found')

    # Check if election has ended
    from datetime import datetime
    if election.ends_at and datetime.now() > election.ends_at:
        raise ValidationError(message='This election has ended. Voting is no longer allowed.', status_code=400)
    
    # Check if election has started
    if election.starts_at and datetime.now() < election.starts_at:
        raise ValidationError(message='This election has not started yet. Please wait until voting begins.', status_code=400)

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

    # Check if voter has already cast any votes
    existing_vote = Vote.query.filter_by(
        election_id=election_id,
        voter_id=voter.id,
        action='vote'
    ).first()
    if existing_vote:
        raise ValidationError(message='You have already voted in this election', status_code=400)

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

    # After creating the voter locally, attempt to register on-chain if election has onchain_id
    try:
        if election.onchain_id:
            cs = ContractService()
            # compute a solidity keccak for voter identity: (uint256 electionId, string registration_number)
            voter_hash = cs.compute_voter_hash(['uint256', 'string'], [int(election.onchain_id), record.registration_number])
            res = cs.send_transaction('registerVoter', [int(election.onchain_id), voter_hash], wait_for_receipt=True, timeout=120)
            tx_hash = res.get('tx_hash')
            receipt = res.get('receipt')

            vote = Vote(
                election_id=election.id,
                voter_id=voter.id,
                candidate_id=None,
                action='register_voter',
                tx_hash=tx_hash,
                status='pending'
            )

            if receipt:
                # sanitize receipt (convert HexBytes/bytes to hex strings)
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
                try:
                    contract = cs.get_contract()
                    events = contract.events.VoterRegistered().process_receipt(receipt)
                    if events:
                        # event args may include voterId; set if present
                        evt = events[0]
                        maybe_id = evt['args'].get('voterId') if 'args' in evt and 'voterId' in evt.get('args', {}) else None
                        if maybe_id is not None:
                            try:
                                voter.onchain_id = int(maybe_id)
                            except Exception:
                                pass
                        vote.status = 'confirmed'
                        vote.block_number = int(receipt.get('blockNumber')) if receipt.get('blockNumber') else None
                except Exception:
                    app.logger.exception('Failed to parse voter registered event')

            db.session.add(vote)
            db.session.add(voter)
            db.session.commit()
    except Exception:
        app.logger.exception('Failed to register voter on-chain')
        # Propagate so caller is aware (per request to not hide errors)
        raise

    return APIResponse.success(message='Voter created', data={'voter': voter.to_dict()}, status_code=201)


@app.route('/api/v1/elections/<int:election_id>/voters', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_voters(election_id):
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')
    voters = Voter.query.filter_by(election_id=election_id).order_by(Voter.id.asc()).all()
    
    # Count cast votes (unique voters who have voted)
    cast_votes_count = db.session.query(Vote.voter_id).filter(
        Vote.election_id == election_id,
        Vote.action == 'vote',
        Vote.voter_id.isnot(None)
    ).distinct().count()
    
    return APIResponse.success(data={
        'voters': [v.to_dict() for v in voters],
        'cast_votes': cast_votes_count
    }, status_code=200)


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


@app.route('/api/v1/elections/<int:election_id>/vote', methods=['POST'], strict_slashes=False)
@jwt_required()
def cast_vote(election_id):
    """Cast votes for the authenticated voter. Expects a JWT with 'vote_auth' claim and 'voter_id'.

    Body: { votes: [{ positionId, selectedCandidate: { id } }, ... ] }
    """
    claims = get_jwt()
    if not claims.get('vote_auth'):
        raise ValidationError(message='Unauthorized to vote', status_code=401)

    token_eid = claims.get('election_id')
    voter_id = claims.get('voter_id')
    if token_eid is None or int(token_eid) != int(election_id):
        raise ValidationError(message='Token election mismatch', status_code=401)

    if voter_id is None:
        raise ValidationError(message='Invalid voter token', status_code=401)

    voter = Voter.query.get(int(voter_id))
    if not voter:
        raise NotFoundError(message='Voter not found')

    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    payload = request.get_json() or {}
    votes = payload.get('votes')
    if not isinstance(votes, list) or len(votes) == 0:
        raise ValidationError(message='No votes provided', status_code=400)

    # Validate votes and prepare on-chain operations
    ops = []
    for v in votes:
        candidate_id = None
        if isinstance(v, dict):
            sel = v.get('selectedCandidate') or v.get('candidate') or v.get('selected')
            if isinstance(sel, dict):
                candidate_id = sel.get('id')
            else:
                candidate_id = sel
        else:
            # legacy: v is candidate id
            candidate_id = v

        if not candidate_id:
            raise ValidationError(message='Invalid vote payload', status_code=400)

        candidate = Candidate.query.get(int(candidate_id))
        if not candidate or candidate.election_id != int(election_id):
            raise ValidationError(message=f'Candidate {candidate_id} invalid for election', status_code=400)

        if candidate.onchain_id is None:
            raise ValidationError(message=f'Candidate {candidate_id} not registered on-chain', status_code=400)

        ops.append({'candidate': candidate})

    # Prepare voter_hash
    if not election.onchain_id:
        raise ValidationError(message='Election not registered on-chain', status_code=400)

    # Need institutional registration number to compute same hash used during registration
    record = InstitutionalRecord.query.get(voter.student_record_id)
    if not record:
        raise ValidationError(message='Voter institutional record not found', status_code=400)

    try:
        cs = ContractService()
    except Exception as e:
        app.logger.exception('ContractService not configured')
        raise

    voter_hash = cs.compute_voter_hash(['uint256', 'string'], [int(election.onchain_id), record.registration_number])

    results = []
    # For each vote, send a transaction calling voteOnBehalf(electionId, voterHash, candidateOnchainId)
    for op in ops:
        candidate = op['candidate']
        try:
            res = cs.send_transaction('voteOnBehalf', [int(election.onchain_id), voter_hash, int(candidate.onchain_id)], wait_for_receipt=True, timeout=120)
            tx_hash = res.get('tx_hash')
            receipt = res.get('receipt')

            # record audit Vote
            vote_record = Vote(
                election_id=election.id,
                voter_id=voter.id,
                candidate_id=candidate.id,
                action='vote',
                tx_hash=tx_hash,
                status='pending'
            )
            if receipt:
                # sanitize receipt
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

                vote_record.receipt = _sanitize(receipt)
                vote_record.status = 'confirmed'
                vote_record.block_number = int(receipt.get('blockNumber')) if receipt.get('blockNumber') else None

            db.session.add(vote_record)
            db.session.commit()
            results.append({'candidate_id': candidate.id, 'tx_hash': tx_hash, 'status': vote_record.status})
        except ContractLogicError as cle:
            # Extract and return a friendly revert reason to the client
            reason = _extract_revert_reason(cle)
            app.logger.warning('Contract reverted while casting vote: %s', reason)
            return APIResponse.error(message=f'Contract error: {reason}', errors={'contract': reason}, status_code=400)
        except Exception as e:
            app.logger.exception('Failed to send vote tx')
            # propagate so client sees the failure
            raise

    return APIResponse.success(message='Votes cast', data={'results': results}, status_code=200)


@app.route('/api/v1/elections/<int:election_id>/audit-auth', methods=['POST'], strict_slashes=False)
def audit_auth(election_id):
    """Authenticate voter for audit page viewing using face recognition.
    
    Returns a short-lived JWT with 'audit_auth' claim that can be used to access the audit endpoint.
    """
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
        raise ValidationError(message='No reference image available for this voter.', status_code=400)

    file = request.files.get('image')
    if not file or not allowed_file(file.filename):
        raise ValidationError(message='Validation failed', errors={'image': 'Invalid image file'}, status_code=400)

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    temp_name = f"audit_live_{uuid.uuid4().hex}.{ext}"
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
            raise ValidationError(message='Face could not be detected in the image', status_code=400)
        except Exception as e:
            raise ValidationError(message=f'Face verification failed: {str(e)}', status_code=500)

        is_match = bool(result.get('verified', False))
        distance = result.get('distance')
        threshold = result.get('threshold')

        if not is_match:
            raise ValidationError(message='Face did not match', errors={"error": "Can not authenticate! Face did not match"}, status_code=401)

        # Create audit token (10 minutes validity)
        token = create_access_token(
            identity=f"voter:{voter.id}",
            additional_claims={'audit_auth': True, 'election_id': election_id, 'voter_id': voter.id},
            expires_delta=timedelta(minutes=10)
        )

        return APIResponse.success(message='Voter authenticated for audit', data={'token': token}, status_code=200)
    finally:
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            app.logger.exception('Failed to remove temporary audit image')


@app.route('/api/v1/elections/<int:election_id>/audit', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_audit(election_id):
    """Get audit information for the authenticated voter.
    
    Returns the list of candidates the voter voted for, along with transaction hashes.
    Requires a JWT with 'audit_auth' claim from the audit-auth endpoint.
    """
    claims = get_jwt()
    if not claims.get('audit_auth'):
        raise ValidationError(message='Unauthorized to view audit', status_code=401)

    token_eid = claims.get('election_id')
    voter_id = claims.get('voter_id')
    if token_eid is None or int(token_eid) != int(election_id):
        raise ValidationError(message='Token election mismatch', status_code=401)

    if voter_id is None:
        raise ValidationError(message='Invalid audit token', status_code=401)

    voter = Voter.query.get(int(voter_id))
    if not voter:
        raise NotFoundError(message='Voter not found')

    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    # Get all vote records for this voter in this election
    votes = Vote.query.filter_by(
        election_id=election_id,
        voter_id=voter.id,
        action='vote'
    ).order_by(Vote.created_at.asc()).all()

    if not votes:
        return APIResponse.success(message='No votes found', data={'votes': [], 'voter': voter.to_dict()}, status_code=200)

    # Build response with candidate details and transaction info
    vote_details = []
    for vote in votes:
        candidate = Candidate.query.get(vote.candidate_id) if vote.candidate_id else None
        post = Post.query.get(candidate.post_id) if candidate else None
        
        vote_detail = {
            'id': vote.id,
            'tx_hash': vote.tx_hash,
            'status': vote.status,
            'block_number': vote.block_number,
            'created_at': vote.created_at.isoformat() if vote.created_at else None,
            'candidate': candidate.to_dict() if candidate else None,
            'position': post.to_dict() if post else None
        }
        vote_details.append(vote_detail)

    return APIResponse.success(
        message='Audit data retrieved',
        data={
            'votes': vote_details,
            'voter': voter.to_dict(),
            'election': election.to_dict()
        },
        status_code=200
    )
