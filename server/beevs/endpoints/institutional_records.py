import io
import csv
from flask import request, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from beevs.response import APIResponse
from beevs import db
from beevs.models import InstitutionalRecord, Election, Admin
from beevs.exceptions import ValidationError, NotFoundError


@app.route('/api/v1/elections/<int:election_id>/institutional-records/upload', methods=['POST'], strict_slashes=False)
@jwt_required()
def upload_institutional_records(election_id):
    """
    Upload a CSV of institutional records for an election. Expects multipart/form-data with a file field named 'file'.

    Required CSV columns (case-insensitive): name, registration_number, department, faculty, level
    """
    # validate election exists
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    if 'file' not in request.files:
        raise ValidationError(message='No file provided', status_code=400)

    file = request.files['file']
    if not file or file.filename == '':
        raise ValidationError(message='No file provided', status_code=400)

    # read CSV
    try:
        stream = io.TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(stream)
    except Exception as e:
        raise ValidationError(message='Failed to read CSV file', errors={'file': str(e)}, status_code=400)

    required_cols = {'name', 'registration_number', 'department', 'faculty', 'level'}
    header_cols = {c.strip().lower() for c in reader.fieldnames or []}
    missing = required_cols - header_cols
    if missing:
        raise ValidationError(message='CSV missing required columns', errors={'missing_columns': list(missing)}, status_code=400)

    saved = []
    errors = []
    seen_reg_nos = set()

    # preload existing registration_numbers for this election to check uniqueness quickly
    try:
        existing_regs = {r[0] for r in InstitutionalRecord.query.with_entities(InstitutionalRecord.registration_number).filter_by(election_id=election_id).all()}
    except Exception:
        existing_regs = set()

    for idx, row in enumerate(reader, start=1):
        # normalize keys
        data = {k.strip().lower(): (v.strip() if v is not None else '') for k, v in row.items()}
        row_errors = {}
        for col in required_cols:
            if not data.get(col):
                row_errors[col] = 'Required field missing'

        # validate level int
        if 'level' not in row_errors:
            try:
                data['level'] = int(data['level'])
            except Exception:
                row_errors['level'] = 'Level must be an integer'

        reg_no = data.get('registration_number')
        if reg_no:
            if reg_no in seen_reg_nos:
                row_errors['registration_number'] = 'Duplicate registration_number in CSV'
            if reg_no in existing_regs:
                row_errors['registration_number'] = 'registration_number already exists for this election'

        if row_errors:
            errors.append({'row': idx, 'errors': row_errors, 'data': data})
            continue

        # create record
        record = InstitutionalRecord(
            name=data['name'],
            registration_number=reg_no,
            department=data['department'],
            faculty=data['faculty'],
            level=data['level'],
            election_id=election_id
        )
        db.session.add(record)
        saved.append(record)
        seen_reg_nos.add(reg_no)

    # commit saved records
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValidationError(message='Failed to save records', errors={'db': str(e)}, status_code=500)

    return APIResponse.success(message='CSV processed', data={'saved_count': len(saved), 'errors': errors, 'saved': [r.to_dict() for r in saved]}, status_code=201)


@app.route('/api/v1/elections/<int:election_id>/institutional-records', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_institutional_records(election_id):
    """List all institutional records for an election."""
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    records = InstitutionalRecord.query.filter_by(election_id=election_id).order_by(InstitutionalRecord.id.asc()).all()
    return APIResponse.success(data={'records': [r.to_dict() for r in records]}, status_code=200)


@app.route('/api/v1/institutional-records/<int:record_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_institutional_record(record_id):
    """Delete a single institutional record by id."""
    record = InstitutionalRecord.query.get(record_id)
    if not record:
        raise NotFoundError(message='Record not found')

    db.session.delete(record)
    db.session.commit()
    return APIResponse.success(message='Record deleted', data=None, status_code=200)


@app.route('/api/v1/elections/<int:election_id>/institutional-records', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_all_institutional_records(election_id):
    """Delete all institutional records for an election."""
    election = Election.query.get(election_id)
    if not election:
        raise NotFoundError(message='Election not found')

    try:
        deleted = InstitutionalRecord.query.filter_by(election_id=election_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValidationError(message='Failed to delete records', errors={'db': str(e)}, status_code=500)

    return APIResponse.success(message='Records deleted', data={'deleted_count': deleted}, status_code=200)
