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