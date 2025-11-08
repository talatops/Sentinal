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
