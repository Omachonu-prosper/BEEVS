from enum import Enum
from datetime import datetime
from beevs import db, bcrypt


class AdminRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    role = db.Column(db.Enum(AdminRole), nullable=False, default=AdminRole.ADMIN)
    
    def __init__(self, name, email, role=AdminRole.ADMIN):
        self.name = name
        self.email = email
        self.role = role
    
    def __repr__(self):
        return f'<Admin {self.name} ({self.email})>'
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")
    
    @password.setter
    def password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password_hash, plain_password)
    
    def to_dict(self):
        """Convert admin object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'role': self.role.value if self.role else None
        }
    
    def is_super_admin(self):
        """Check if admin has super admin privileges"""
        return self.role == AdminRole.SUPER_ADMIN


class Election(db.Model):
    __tablename__ = 'elections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    scheduled_for = db.Column(db.Date, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    super_admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)

    super_admin = db.relationship('Admin', backref=db.backref('elections', lazy=True))

    def __repr__(self):
        return f'<Election {self.title} ({self.id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'super_admin_id': self.super_admin_id
        }


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False)

    election = db.relationship('Election', backref=db.backref('posts', lazy=True, passive_deletes=True))

    def to_dict(self, include_counts=False):
        base = {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'election_id': self.election_id
        }
        if include_counts:
            base['candidate_count'] = len(self.__dict__.get('candidates', []))
        return base


class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    wallet_address = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    election = db.relationship('Election', backref=db.backref('candidates', lazy=True, passive_deletes=True))
    post = db.relationship('Post', backref=db.backref('candidates', lazy=True, passive_deletes=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'wallet_address': self.wallet_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'election_id': self.election_id,
            'post_id': self.post_id
        }


class InstitutionalRecord(db.Model):
    __tablename__ = 'institutional_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    registration_number = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(255), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False)

    election = db.relationship('Election', backref=db.backref('institutional_records', lazy=True, passive_deletes=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration_number': self.registration_number,
            'department': self.department,
            'faculty': self.faculty,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'election_id': self.election_id
        }


class Voter(db.Model):
    __tablename__ = 'voters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    wallet_address = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False)
    student_record_id = db.Column(db.Integer, db.ForeignKey('institutional_records.id', ondelete='CASCADE'), nullable=False)

    election = db.relationship('Election', backref=db.backref('voters', lazy=True, passive_deletes=True))
    student_record = db.relationship('InstitutionalRecord', backref=db.backref('voter', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'image_url': self.image_url,
            'wallet_address': self.wallet_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'election_id': self.election_id,
            'student_record_id': self.student_record_id
        }