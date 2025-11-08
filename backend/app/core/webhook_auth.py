"""Webhook authentication middleware."""
from functools import wraps
from flask import request, jsonify
from app.models.api_token import APIToken


def webhook_auth_required(f):
    """Decorator to require API token authentication for webhooks."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        else:
            token = request.headers.get('X-API-Token') or request.headers.get('Authorization', '')
        
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

