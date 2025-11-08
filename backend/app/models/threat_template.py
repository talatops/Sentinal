"""Threat template model for pre-built threat templates."""
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB


class ThreatTemplate(db.Model):
    """Model for threat templates."""
    __tablename__ = 'threat_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)  # 'web_app', 'api', 'database', 'auth'
    asset_type = db.Column(db.String(100), nullable=True)
    flow_template = db.Column(db.Text, nullable=False)
    trust_boundary_template = db.Column(db.String(200), nullable=True)
    stride_categories = db.Column(JSONB, nullable=True)  # Suggested STRIDE categories
    default_dread_scores = db.Column(JSONB, nullable=True)  # Default DREAD scores
    default_mitigation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ThreatTemplate {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'asset_type': self.asset_type,
            'flow_template': self.flow_template,
            'trust_boundary_template': self.trust_boundary_template,
            'stride_categories': self.stride_categories,
            'default_dread_scores': self.default_dread_scores,
            'default_mitigation': self.default_mitigation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

