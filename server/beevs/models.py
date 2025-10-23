from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()


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
    
    def __init__(self, name, email, password_hash, role=AdminRole.ADMIN):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
    
    def __repr__(self):
        return f'<Admin {self.name} ({self.email})>'
    
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