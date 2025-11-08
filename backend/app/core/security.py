"""Security utilities for authentication and authorization."""
import bcrypt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import json
from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from app.models.user import User


def jwt_required(f=None, **kwargs):
    """Custom JWT required decorator that returns proper 401 responses for Flask-RESTful.

    Supports both @jwt_required and @jwt_required() syntax.
    For refresh tokens, use Flask-JWT-Extended's jwt_required directly in auth.py.
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **func_kwargs):
            try:
                verify_jwt_in_request()
                return func(*args, **func_kwargs)
            except (NoAuthorizationError, JWTDecodeError, ExpiredSignatureError, InvalidTokenError) as e:
                error_message = str(e)
                auth_header_msg = 'Missing Authorization Header' in error_message
                auth_header_missing = 'Authorization header is missing' in error_message
                if auth_header_msg or auth_header_missing:
                    return {'error': 'Authorization header is missing'}, 401
                elif ('expired' in error_message.lower() or
                      isinstance(e, ExpiredSignatureError)):
                    return {'error': 'Token has expired'}, 401
                elif ('invalid' in error_message.lower() or
                      isinstance(e, (JWTDecodeError, InvalidTokenError))):
                    return {'error': 'Invalid token'}, 401
                else:
                    return {'error': 'Authentication required'}, 401
        return decorated_function

    if f is None:
        # Called as @jwt_required()
        return decorator
    else:
        # Called as @jwt_required
        return decorator(f)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS."""
    if not isinstance(input_str, str):
        return str(input_str)

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()


def encode_output(text: str) -> str:
    """Encode output to prevent XSS attacks."""
    if not isinstance(text, str):
        text = str(text)

    # HTML entity encoding
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;',
    }

    for char, entity in replacements.items():
        text = text.replace(char, entity)

    return text


def role_required(required_role: str):
    """Decorator to require a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if user.role != required_role and user.role != 'Admin':
                return jsonify({'error': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required('Admin')(f)


def log_security_event(event_type: str, user_id: int, details: dict = None):
    """Log security events for audit trail."""
    current_app.logger.info(
        json.dumps({
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'details': details or {}
        })
    )
