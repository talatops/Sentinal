"""Requirement and SecurityControl models."""
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB


class Requirement(db.Model):
    """Requirement model with security controls."""
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    security_controls = db.Column(JSONB, nullable=False)  # Array of security control IDs
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Draft', nullable=False)
    owasp_asvs_level = db.Column(db.String(20), nullable=True)  # Level 1, 2, or 3
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    controls = db.relationship('SecurityControl', backref='requirement', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Requirement {self.title}>'
    
    def to_dict(self):
        """Convert requirement to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'security_controls': self.security_controls,
            'created_by': self.created_by,
            'status': self.status,
            'owasp_asvs_level': self.owasp_asvs_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'controls': [control.to_dict() for control in self.controls]
        }


class SecurityControl(db.Model):
    """Security control model linked to requirements."""
    __tablename__ = 'security_controls'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owasp_asvs_level = db.Column(db.String(20), nullable=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SecurityControl {self.name}>'
    
    def to_dict(self):
        """Convert security control to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owasp_asvs_level': self.owasp_asvs_level,
            'requirement_id': self.requirement_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

