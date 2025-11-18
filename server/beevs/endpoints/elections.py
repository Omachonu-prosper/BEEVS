from flask import current_app as app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from beevs.response import APIResponse
from beevs import db
from beevs.models import Election
from beevs.exceptions import ValidationError, AuthorizationError
from datetime import datetime
from beevs.contract import ContractService
from beevs.models import Vote
from flask import current_app as app


def _sanitize_for_json(obj):
    """Recursively convert web3/eth types (HexBytes, bytes) into JSON-serializable forms.

    - bytes/bytearray/HexBytes -> 0x-prefixed hex string
    - lists/dicts -> processed recursively
    - other scalars returned unchanged
    """
    # Avoid importing HexBytes directly to keep dependencies minimal
    from hexbytes import HexBytes as _HexBytes
    # AttributeDict and other dict-like structures may not be plain dicts

    if obj is None:
        return None

    # Convert bytes-like to hex
    if isinstance(obj, _HexBytes) or isinstance(obj, (bytes, bytearray)):
        try:
            return '0x' + bytes(obj).hex()
        except Exception:
            return str(obj)

    # Lists/tuples/sets -> sanitize elements
    if isinstance(obj, (list, tuple, set)):
        return [ _sanitize_for_json(v) for v in obj ]

    # Dict-like objects (including web3 AttributeDict) -> sanitize key/values
    if hasattr(obj, 'items'):
        result = {}
        try:
            for k, v in dict(obj).items():
                result[k] = _sanitize_for_json(v)
            return result
        except Exception:
            # Fallthrough to str conversion
            return str(obj)

    # Primitive types that are JSON-serializable
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Unknown types -> string representation
    try:
        return str(obj)
    except Exception:
        return None


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

    # After creating the DB record, create the election on-chain using the relayer
    try:
        cs = ContractService()
    except Exception as e:
        app.logger.exception('ContractService not configured')
        return APIResponse.error(message='Election created locally but contract service not configured', errors={'error': str(e), 'election': election.to_dict()}, status_code=201)

    # determine timestamps
    if election.starts_at:
        start_ts = int(election.starts_at.timestamp())
    elif election.scheduled_for:
        start_ts = int(datetime.combine(election.scheduled_for, datetime.min.time()).timestamp())
    else:
        start_ts = 0

    if election.ends_at:
        end_ts = int(election.ends_at.timestamp())
    else:
        end_ts = 0

    try:
        res = cs.send_transaction('createElection', [election.title, start_ts, end_ts], wait_for_receipt=True, timeout=180)
    except Exception as e:
        app.logger.exception('Failed to send createElection tx')
        return APIResponse.error(message='Election created locally but failed to create on-chain', errors={'error': str(e)}, status_code=500)

    tx_hash = res.get('tx_hash')
    receipt = res.get('receipt')

    # record vote/tx
    vote = Vote(
        election_id=election.id,
        voter_id=None,
        candidate_id=None,
        action='create_election',
        tx_hash=tx_hash,
        status='pending'
    )

    if receipt:
        try:
            contract = cs.get_contract()
            live_receipt = cs.wait_for_receipt(tx_hash, timeout=10)
            events = []
            if live_receipt:
                events = contract.events.ElectionCreated().process_receipt(live_receipt)
            else:
                try:
                    events = contract.events.ElectionCreated().process_receipt(receipt)
                except Exception:
                    events = []

            if events:
                evt = events[0]
                onchain_id = int(evt['args']['electionId'])
                election.onchain_id = onchain_id
                vote.status = 'confirmed'
                vote.block_number = int(receipt.get('blockNumber')) if receipt.get('blockNumber') else None
                vote.receipt = _sanitize_for_json(receipt)
            else:
                vote.status = 'pending'
                vote.receipt = _sanitize_for_json(receipt)
        except Exception:
            vote.status = 'pending'
            vote.receipt = _sanitize_for_json(receipt)
            app.logger.exception('Failed to parse receipt or event')

    db.session.add(vote)
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


@app.route('/api/v1/elections/<int:election_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_election(election_id):
    """Return a single election with some useful counts (candidates, voters, posts).

    This is a lightweight endpoint used by the frontend DetailsTab to show metadata
    about a specific election.
    """
    # identity stored as string in token
    admin_id_raw = get_jwt_identity()
    try:
        admin_id = int(admin_id_raw)
    except Exception:
        raise AuthorizationError(message='Invalid token identity')

    election = Election.query.get(election_id)
    if not election:
        return APIResponse.error(message='Election not found', status_code=404)

    # Compute some quick counts. Relationships use lazy loading so these will be simple
    # attribute accesses that load the related rows.
    candidate_count = len(election.candidates) if hasattr(election, 'candidates') else 0
    voter_count = len(election.voters) if hasattr(election, 'voters') else 0
    post_count = len(election.posts) if hasattr(election, 'posts') else 0
    
    # Count cast votes (unique voters who have cast at least one vote)
    cast_votes_count = db.session.query(Vote.voter_id).filter(
        Vote.election_id == election_id,
        Vote.action == 'vote',
        Vote.voter_id.isnot(None)
    ).distinct().count()

    payload = election.to_dict()
    payload.update({
        'candidate_count': candidate_count,
        'voter_count': voter_count,
        'post_count': post_count,
        'cast_votes': cast_votes_count
    })

    return APIResponse.success(message='Election fetched', data={'election': payload}, status_code=200)


@app.route('/api/v1/elections/<int:election_id>/results', methods=['GET'], strict_slashes=False)
def get_election_results(election_id):
    """Get election results grouped by posts with vote counts for each candidate.
    
    This endpoint aggregates votes from the Vote table and fetches on-chain data
    if available. Returns results structured by posts/positions.
    """
    from beevs.models import Post, Candidate, Vote
    
    election = Election.query.get(election_id)
    if not election:
        return APIResponse.error(message='Election not found', status_code=404)
    
    # Get all posts for this election with their candidates
    posts = Post.query.filter_by(election_id=election_id).order_by(Post.id.asc()).all()
    
    results = []
    for post in posts:
        candidates_data = []
        
        # Get all candidates for this post
        candidates = Candidate.query.filter_by(post_id=post.id).order_by(Candidate.id.asc()).all()
        
        for candidate in candidates:
            # Count votes for this candidate from the Vote table
            vote_count = db.session.query(Vote).filter(
                Vote.candidate_id == candidate.id,
                Vote.action == 'vote',
                Vote.status == 'confirmed'
            ).count()
            
            # Try to get on-chain vote count if available
            onchain_votes = None
            if election.onchain_id and candidate.onchain_id:
                try:
                    cs = ContractService()
                    # Call contract.getCandidate(electionId, candidateId) -> (name, voteCount)
                    result = cs.call('getCandidate', election.onchain_id, candidate.onchain_id)
                    if result and len(result) >= 2:
                        onchain_votes = int(result[1])
                except Exception as e:
                    app.logger.warning(f'Failed to fetch on-chain votes for candidate {candidate.id}: {e}')
            
            candidates_data.append({
                'id': candidate.id,
                'name': candidate.name,
                'image_url': candidate.image_url,
                'votes': onchain_votes if onchain_votes is not None else vote_count,
                'onchain_votes': onchain_votes,
                'db_votes': vote_count
            })
        
        # Sort candidates by votes descending
        candidates_data.sort(key=lambda x: x['votes'], reverse=True)
        
        results.append({
            'id': post.id,
            'title': post.title,
            'candidates': candidates_data,
            'winner': candidates_data[0]['name'] if candidates_data else None
        })
    
    return APIResponse.success(
        message='Election results fetched',
        data={
            'election': election.to_dict(),
            'results': results
        },
        status_code=200
    )
