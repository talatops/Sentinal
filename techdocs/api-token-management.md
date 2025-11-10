# API Token Management System for Webhook Authentication

## Overview

Create a secure API token system for authenticating GitHub Actions webhooks and other external integrations. This will allow GitHub Actions to securely send scan results to the dashboard.

**Token Format:**
- Tokens are prefixed with `sent_` followed by a 32-byte URL-safe random string
- Token prefix (first 12 characters: `sent_` + 7 chars) is stored in the database for identification
- Full tokens are only shown once during creation and are never stored in plaintext
- Tokens are hashed using SHA-256 before storage

## Architecture

### Components Needed:

1. **API Token Model** - Database model to store tokens
2. **Token Generation** - Endpoint to create new tokens
3. **Token Management** - Endpoints to list, revoke, and manage tokens
4. **Webhook Authentication** - Middleware to verify tokens
5. **Admin UI** - Frontend interface to manage tokens (optional)

---

## Implementation Plan

### Phase 1: Database Model

**File:** `backend/app/models/api_token.py` (new)

```python
"""API Token model for webhook authentication."""
from datetime import datetime
from app import db
import secrets
import hashlib

class APIToken(db.Model):
    """API Token model for external integrations."""
    __tablename__ = 'api_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "GitHub Actions CI/CD"
    token_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    token_prefix = db.Column(db.String(15), nullable=False)  # "sent_" + up to 10 chars (12 chars total)
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
        token_prefix = token[:12]  # "sent_" + 7 chars = 12 chars total
        return token, token_hash, token_prefix
    
    @staticmethod
    def verify_token(token: str) -> 'APIToken':
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
```

**Migration:** Create migration to add `api_tokens` table

---

### Phase 2: Token Management API Endpoints

**File:** `backend/app/api/api_tokens.py` (new)

```python
"""API Token management endpoints."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from app.core.security import jwt_required
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.api_token import APIToken
from app.models.user import User
from datetime import datetime, timedelta

class CreateTokenSchema(Schema):
    """Schema for creating API token."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    expires_in_days = fields.Int(missing=None, allow_none=True)  # None = never expires
    scopes = fields.List(fields.Str(), missing=['webhook:write'])

class CreateAPIToken(Resource):
    """Create a new API token."""
    
    @jwt_required()
    def post(self):
        """Create a new API token."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'Admin':
            return {'error': 'Admin access required'}, 403
        
        schema = CreateTokenSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Generate token
        token, token_hash, token_prefix = APIToken.generate_token()
        
        # Calculate expiration
        expires_at = None
        if data.get('expires_in_days'):
            expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])
        
        # Create token record
        api_token = APIToken(
            name=data['name'],
            token_hash=token_hash,
            token_prefix=token_prefix,
            created_by=user_id,
            expires_at=expires_at,
            scopes=','.join(data.get('scopes', ['webhook:write']))
        )
        db.session.add(api_token)
        db.session.commit()
        
        # Return token (only shown once!)
        return {
            'token': token,
            'token_info': api_token.to_dict()
        }, 201

class ListAPITokens(Resource):
    """List all API tokens."""
    
    @jwt_required()
    def get(self):
        """List all API tokens."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'Admin':
            return {'error': 'Admin access required'}, 403
        
        tokens = APIToken.query.order_by(APIToken.created_at.desc()).all()
        return {'tokens': [token.to_dict() for token in tokens]}, 200

class RevokeAPIToken(Resource):
    """Revoke an API token."""
    
    @jwt_required()
    def post(self, token_id):
        """Revoke an API token."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'Admin':
            return {'error': 'Admin access required'}, 403
        
        api_token = APIToken.query.get_or_404(token_id)
        api_token.is_active = False
        db.session.commit()
        
        return {'message': 'Token revoked successfully'}, 200
```

**File:** `backend/app/api/__init__.py`

Add token routes:
```python
from app.api import api_tokens

api.add_resource(api_tokens.CreateAPIToken, '/auth/api-tokens')
api.add_resource(api_tokens.ListAPITokens, '/auth/api-tokens')
api.add_resource(api_tokens.RevokeAPIToken, '/auth/api-tokens/<int:token_id>/revoke')
```

---

### Phase 3: Webhook Authentication Middleware

**File:** `backend/app/core/webhook_auth.py` (new)

```python
"""Webhook authentication middleware."""
from functools import wraps
from flask import request, jsonify
from app.models.api_token import APIToken

def webhook_auth_required(f):
    """Decorator to require API token authentication for webhooks."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        token = request.headers.get('X-API-Token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'API token required'}), 401
        
        # Verify token
        api_token = APIToken.verify_token(token)
        
        if not api_token:
            return jsonify({'error': 'Invalid or expired API token'}), 401
        
        # Check scopes
        required_scope = 'webhook:write'
        scopes = api_token.scopes.split(',') if api_token.scopes else []
        if required_scope not in scopes and 'webhook:*' not in scopes:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Attach token info to request
        request.api_token = api_token
        
        return f(*args, **kwargs)
    return decorated_function
```

**File:** `backend/app/api/cicd.py`

Update webhook endpoints to use authentication:
```python
from app.core.webhook_auth import webhook_auth_required

class CICDWebhook(Resource):
    """Webhook endpoint for receiving CI/CD scan results."""
    
    @webhook_auth_required
    def post(self, scan_type):
        """Receive scan results from GitHub Actions."""
        # api_token is available via request.api_token
        data = request.json
        # ... rest of implementation
```

---

### Phase 4: Configuration

**File:** `backend/app/core/config.py`

Add webhook configuration:
```python
# Webhook Configuration
WEBHOOK_API_ENABLED = os.environ.get('WEBHOOK_API_ENABLED', 'true').lower() == 'true'
WEBHOOK_RATE_LIMIT = os.environ.get('WEBHOOK_RATE_LIMIT', '100 per hour')
```

**File:** `.docker.env`

Add webhook configuration (optional):
```bash
# Webhook API Configuration
WEBHOOK_API_ENABLED=true
WEBHOOK_RATE_LIMIT=100 per hour
```

---

### Phase 5: Frontend Token Management UI (Optional)

**File:** `frontend/src/pages/APITokens.jsx` (new)

Features:
- List all API tokens
- Create new token (show token once)
- Revoke tokens
- View token details (prefix, scopes, last used)
- Copy token to clipboard

---

## Usage Flow

### Step 1: Admin Creates API Token

**Via API:**
```bash
POST /api/auth/api-tokens
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "name": "GitHub Actions CI/CD",
  "expires_in_days": 365,
  "scopes": ["webhook:write"]
}

Response:
{
  "token": "sent_abc123xyz...",
  "token_info": {
    "id": 1,
    "name": "GitHub Actions CI/CD",
    "token_prefix": "sent_abc1",
    "created_by": 1,
    "expires_at": "2026-11-10T13:00:00",
    "last_used_at": null,
    "is_active": true,
    "scopes": ["webhook:write"],
    "created_at": "2025-11-10T13:00:00"
  }
}
```

**Via UI (if implemented):**
- Admin logs in → Settings → API Tokens
- Click "Create New Token"
- Enter name: "GitHub Actions CI/CD"
- Set expiration (optional)
- Select scopes
- Copy token immediately (shown only once)

### Step 2: Add Token to GitHub Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add new secret:
   - Name: `SENTINAL_API_TOKEN`
   - Value: `sent_abc123xyz...` (the token from step 1)
3. Add API URL secret:
   - Name: `SENTINAL_API_URL`
   - Value: `https://your-sentinal-api.com` (or `http://localhost/api` for local)

### Step 3: GitHub Actions Uses Token

```yaml
- name: Send Results to Dashboard
  run: |
    curl -X POST "${{ secrets.SENTINAL_API_URL }}/api/cicd/webhook/sonarqube" \
      -H "Content-Type: application/json" \
      -H "X-API-Token: ${{ secrets.SENTINAL_API_TOKEN }}" \
      -d '{...}'
```

### Step 4: Backend Validates Token

1. Webhook receives request
2. Extracts token from `X-API-Token` header
3. Verifies token hash in database
4. Checks expiration
5. Validates scopes
6. Updates last_used_at
7. Processes webhook

---

## Security Features

1. **Token Hashing:** Tokens stored as SHA-256 hashes (never plaintext)
2. **Token Prefix:** Tokens prefixed with `sent_` followed by 7 characters (12 chars total shown in UI for identification)
3. **Expiration:** Optional expiration dates (set via `expires_in_days` parameter)
4. **Scopes:** Fine-grained permissions (webhook:write, webhook:read)
5. **Revocation:** Tokens can be revoked without deletion (sets `is_active=False`)
6. **Last Used Tracking:** Monitor token usage via `last_used_at` field
7. **Rate Limiting:** Apply rate limits to webhook endpoints
8. **Admin Only:** Only admins can create/manage tokens

---

## Database Migrations

### Initial Migration: `002_add_api_tokens.py`

**File:** `backend/migrations/versions/002_add_api_tokens.py`

Creates the initial `api_tokens` table with `token_prefix` as `VARCHAR(10)`.

### Column Size Update: `005_increase_token_prefix_length.py`

**File:** `backend/migrations/versions/005_increase_token_prefix_length.py`

Updates the `token_prefix` column from `VARCHAR(10)` to `VARCHAR(15)` to accommodate the full token prefix format (`sent_` + 7 chars = 12 chars total).

```python
"""Increase token_prefix column length."""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('api_tokens', 'token_prefix',
                    existing_type=sa.String(length=10),
                    type_=sa.String(length=15),
                    existing_nullable=False)

def downgrade():
    op.alter_column('api_tokens', 'token_prefix',
                    existing_type=sa.String(length=15),
                    type_=sa.String(length=10),
                    existing_nullable=False)
```

**Note:** This migration was added to fix an issue where the token generation creates 12-character prefixes but the original column only allowed 10 characters.

---

## Alternative: Simple Static Token (Quick Start)

If you want a quick solution without database:

**File:** `.docker.env`
```bash
WEBHOOK_API_TOKEN=your_static_token_here_32_chars_min
```

**File:** `backend/app/core/webhook_auth.py`
```python
from flask import request, jsonify, current_app

def webhook_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        expected_token = current_app.config.get('WEBHOOK_API_TOKEN')
        
        if not token or token != expected_token:
            return jsonify({'error': 'Invalid API token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

**Pros:** Simple, fast to implement
**Cons:** No token management, no revocation, no tracking

---

## Recommended Approach

**For MVP:** Use Simple Static Token (quick to implement)
**For Production:** Use Full API Token System (better security and management)

---

## Implementation Checklist

### Backend:
- [x] Create `APIToken` model (`backend/app/models/api_token.py`)
- [x] Create migration for `api_tokens` table (`002_add_api_tokens.py`)
- [x] Create migration to increase token_prefix column size (`005_increase_token_prefix_length.py`)
- [x] Create token management API endpoints (`backend/app/api/api_tokens.py`)
- [x] Create webhook authentication middleware (`backend/app/core/webhook_auth.py`)
- [x] Add webhook endpoints with authentication (`backend/app/api/cicd.py`)
- [x] Add rate limiting for webhooks (via Flask-Limiter)
- [x] Add logging for token usage (`last_used_at` tracking)

### Frontend:
- [x] Create API Tokens management page (`frontend/src/pages/APITokens.jsx`)
- [x] Add token creation form
- [x] Add token list with revoke functionality
- [x] Add copy-to-clipboard functionality

### Documentation:
- [x] Document token creation process
- [x] Document GitHub Actions integration
- [x] Document security best practices

---

## Security Best Practices

1. **Never log full tokens** - Only log token prefix
2. **Store tokens securely** - Use GitHub Secrets
3. **Rotate tokens regularly** - Set expiration dates
4. **Use least privilege** - Grant minimum required scopes
5. **Monitor usage** - Track last_used_at for suspicious activity
6. **Revoke compromised tokens** - Immediate revocation capability
7. **Rate limit webhooks** - Prevent abuse
8. **Use HTTPS** - Always use HTTPS in production

