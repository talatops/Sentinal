"""Threat model for STRIDE/DREAD analysis."""
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB


class Threat(db.Model):
    """Threat model for threat modeling."""
    __tablename__ = 'threats'
    
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(200), nullable=False)
    flow = db.Column(db.Text, nullable=False)
    trust_boundary = db.Column(db.String(200), nullable=True)
    stride_categories = db.Column(JSONB, nullable=False)  # Array of STRIDE categories
    dread_score = db.Column(JSONB, nullable=False)  # DREAD scoring details
    risk_level = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    mitigation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Threat {self.asset}>'
    
    def to_dict(self):
        """Convert threat to dictionary."""
        return {
            'id': self.id,
            'asset': self.asset,
            'flow': self.flow,
            'trust_boundary': self.trust_boundary,
            'stride_categories': self.stride_categories,
            'dread_score': self.dread_score,
            'risk_level': self.risk_level,
            'mitigation': self.mitigation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

