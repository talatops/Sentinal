"""API Token model for webhook authentication."""
from datetime import datetime, timedelta
from app import db
import secrets
import hashlib


class APIToken(db.Model):
    """API Token model for external integrations."""
    __tablename__ = 'api_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "GitHub Actions CI/CD"
    token_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    token_prefix = db.Column(db.String(10), nullable=False)  # First 8 chars for display
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # None = never expires
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    scopes = db.Column(db.String(255), nullable=False)  # Comma-separated: webhook:write,webhook:read
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='api_tokens')
    
    @staticmethod
    def generate_token() -> tuple:
        """Generate a new API token.
        
        Returns:
            tuple: (full_token, token_hash, token_prefix)
        """
        # Generate 32-byte random token with prefix
        token = f"sent_{secrets.token_urlsafe(32)}"
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_prefix = token[:12]  # "sent_" + 7 chars
        return token, token_hash, token_prefix
    
    @staticmethod
    def verify_token(token: str):
        """Verify a token and return the token object.
        
        Args:
            token: The API token to verify
            
        Returns:
            APIToken object if valid, None otherwise
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        api_token = APIToken.query.filter_by(
            token_hash=token_hash,
            is_active=True
        ).first()
        
        if not api_token:
            return None
        
        # Check expiration
        if api_token.expires_at and api_token.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_token.last_used_at = datetime.utcnow()
        db.session.commit()
        
        return api_token
    
    def to_dict(self, include_token=False):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'token_prefix': self.token_prefix,
            'created_by': self.created_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_active': self.is_active,
            'scopes': self.scopes.split(',') if self.scopes else [],
            'created_at': self.created_at.isoformat(),
            'token': f'{self.token_prefix}...' if not include_token else None
        }

